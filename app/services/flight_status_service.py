"""Статус рейса через AeroDataBox"""

from datetime import datetime, timedelta

import requests

from app.config import AERODATABOX_API_KEY, AERODATABOX_HOST
from app.models.transport import Transport

DELAY_THRESHOLD_MINUTES = 15
REQUEST_TIMEOUT_SECONDS = 8


class FlightServiceError(Exception):
    """Сервис статусов не ответил или отказал в запросе"""


def _parse_local(value: str | None) -> datetime | None:
    """Переводит местное время из ответа AeroDataBox (2026-11-02 21:55+03:00) в datetime"""

    if not value:
        return None
    return datetime.strptime(value[:16], "%Y-%m-%d %H:%M")


def _pick_closest_flight(flights: list[dict], target_departure: datetime) -> dict | None:
    """Из нескольких рейсов с одним номером берёт тот, чей вылет ближе к нашему времени"""

    if not flights:
        return None

    def time_gap(flight: dict) -> timedelta:
        scheduled = _parse_local(flight.get("departure", {}).get("scheduledTime", {}).get("local"))
        return abs(scheduled - target_departure) if scheduled else timedelta.max

    return min(flights, key=time_gap)


def _map_raw_status(raw_status: str) -> str | None:
    """Переводит статус AeroDataBox в наш (или None, если статус непонятный)"""

    normalized = raw_status.lower()
    if "cancel" in normalized:
        return "cancelled"
    if "landed" in normalized or "arrived" in normalized:
        return "landed"
    if "enroute" in normalized or "en route" in normalized or "departed" in normalized or "diverted" in normalized or "approaching" in normalized:
        return "en_route"
    if "delay" in normalized:
        return "delayed"
    return None


def _build_summary(flight: dict, departure_time: datetime | None) -> str:
    """Что нашлось по номеру рейса: номер, маршрут и время вылета"""

    origin = flight.get("departure", {}).get("airport", {}).get("iata") or "?"
    destination = flight.get("arrival", {}).get("airport", {}).get("iata") or "?"
    time_text = departure_time.strftime("%d.%m.%Y %H:%M") if departure_time else "время неизвестно"
    return f"{flight.get('number', '')}, {origin} → {destination}, вылет {time_text}"


def _extract_status_and_time(flight: dict) -> dict:
    """Достаёт статус и новое время вылета из ответа AeroDataBox"""

    departure = flight.get("departure", {})
    scheduled = _parse_local(departure.get("scheduledTime", {}).get("local"))
    revised = _parse_local(departure.get("revisedTime", {}).get("local"))

    status = _map_raw_status(flight.get("status") or "")
    if status is None:
        # статус не назван - смотрим на разницу во времени вылета
        if scheduled and revised and revised - scheduled >= timedelta(minutes=DELAY_THRESHOLD_MINUTES):
            status = "delayed"
        else:
            status = "scheduled"

    actual_departure = revised if revised and revised != scheduled else None

    return {
        "status": status,
        "actual_departure_datetime": actual_departure,
        "summary": _build_summary(flight, revised or scheduled),
    }


def fetch_real_status(transport: Transport) -> dict | None:
    """Запрашивает у AeroDataBox статус рейса. Возвращает None, если рейс не найден"""

    if not AERODATABOX_API_KEY or transport.type != "Самолёт" or not transport.ticket_number:
        return None
    if not transport.departure_datetime:
        return None

    flight_number = transport.ticket_number.replace(" ", "")
    date_local = transport.departure_datetime.strftime("%Y-%m-%d")
    url = f"https://{AERODATABOX_HOST}/flights/number/{flight_number}/{date_local}"
    params = {
        "withAircraftImage": "false",
        "withFlightPlan": "false",
        "withLocation": "false",
        "dateLocalRole": "Both",
    }
    headers = {"x-rapidapi-host": AERODATABOX_HOST, "x-rapidapi-key": AERODATABOX_API_KEY}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        if response.status_code in (204, 404):
            return None
        response.raise_for_status()
        flights = response.json()
    except (requests.RequestException, ValueError) as error:
        print(f"[TripHelper] AeroDataBox не ответил по рейсу {flight_number}: {error}")
        raise FlightServiceError from error

    flight = _pick_closest_flight(flights, transport.departure_datetime)
    return _extract_status_and_time(flight) if flight else None
