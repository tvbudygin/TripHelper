"""Статус рейса через Aviationstack"""

import re
from datetime import datetime, timedelta

import requests

from app.config import AVIATIONSTACK_API_KEY
from app.models.transport import Transport

API_URL = "https://api.aviationstack.com/v1/flights"
REQUEST_TIMEOUT_SECONDS = 15
DELAY_THRESHOLD_MINUTES = 15


class FlightServiceError(Exception):
    """Ошибка сервиса с понятным сообщением для пользователя"""


def _parse_local(value: str | None) -> datetime | None:
    """Читает время аэропорта из ответа API без дополнительного сдвига"""
    if not value:
        return None
    try:
        # Aviationstack может помечать местные часы как +00:00
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        raise FlightServiceError("API вернул некорректное время рейса") from None


def _pick_closest_flight(flights: list[dict], transport: Transport) -> dict | None:
    """Выбирает рейс нужной даты, а при нескольких вариантах сравнивает время и аэропорты"""
    candidates = []
    date_text = transport.departure_datetime.date().isoformat()
    for flight in flights:
        departure = flight.get("departure") or {}
        arrival = flight.get("arrival") or {}
        scheduled = _parse_local(departure.get("scheduled"))
        flight_date = flight.get("flight_date") or (scheduled.date().isoformat() if scheduled else None)
        if flight_date != date_text:
            continue
        # Если пользователь указал код аэропорта, исключаем другой участок маршрута
        mismatch = False
        for entered, airport in ((transport.departure_airport, departure), (transport.arrival_airport, arrival)):
            text = (entered or "").strip().upper()
            match = re.search(r"\(([A-Z]{3,4})\)", text)
            code = match.group(1) if match else text
            if re.fullmatch(r"[A-Z]{3,4}", code) and code not in (airport.get("iata"), airport.get("icao")):
                mismatch = True
        if not mismatch:
            gap = abs(scheduled - transport.departure_datetime) if scheduled else timedelta.max
            candidates.append((gap, flight))
    return min(candidates, key=lambda item: item[0])[1] if candidates else None


def _extract_status_and_time(flight: dict) -> dict:
    """Преобразует ответ Aviationstack в поля перемещения"""
    departure = flight.get("departure") or {}
    arrival = flight.get("arrival") or {}
    scheduled = _parse_local(departure.get("scheduled"))
    actual = _parse_local(departure.get("actual"))
    estimated = _parse_local(departure.get("estimated"))
    revised = actual or estimated
    delay = departure.get("delay") or 0
    if not revised and scheduled and delay > 0:
        revised = scheduled + timedelta(minutes=delay)

    raw_status = flight.get("flight_status")
    status = {
        "scheduled": "scheduled", "active": "en_route", "landed": "landed",
        "cancelled": "cancelled", "incident": "changed", "diverted": "changed",
    }.get(raw_status)
    if status is None:
        raise FlightServiceError("API пока не сообщил статус этого рейса")
    if status == "scheduled" and (
        delay >= DELAY_THRESHOLD_MINUTES
        or (scheduled and revised and revised - scheduled >= timedelta(minutes=DELAY_THRESHOLD_MINUTES))
    ):
        status = "delayed"

    flight_info = flight.get("flight") or {}
    number = flight_info.get("iata") or flight_info.get("icao") or flight_info.get("number") or ""
    time = revised or scheduled
    time_text = time.strftime("%d.%m.%Y %H:%M") if time else "время неизвестно"
    return {
        "status": status,
        "actual_departure_datetime": revised if revised and revised != scheduled else None,
        "summary": f"{number}, {departure.get('iata') or '?'} → {arrival.get('iata') or '?'}, вылет {time_text}",
    }


def fetch_real_status(transport: Transport) -> dict | None:
    """Получает текущие данные рейса и сверяет их с датой поездки"""
    if transport.type != "Самолёт" or not transport.ticket_number or not transport.departure_datetime:
        raise FlightServiceError("Для проверки укажите самолёт, номер рейса и дату вылета")
    if not AVIATIONSTACK_API_KEY:
        raise FlightServiceError("Ключ сервиса статусов рейсов не настроен")

    number = "".join(transport.ticket_number.upper().split())
    if not re.fullmatch(r"[A-Z0-9]{2,3}[0-9]{1,4}[A-Z]?", number):
        raise FlightServiceError("Укажите номер рейса латиницей, например SU1462")
    field = "flight_icao" if re.match(r"^[A-Z]{3}[0-9]", number) else "flight_iata"
    # flight_date включает платный исторический поиск, поэтому дату сверяем в ответе
    params = {"access_key": AVIATIONSTACK_API_KEY, field: number}
    try:
        response = requests.get(API_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        payload = response.json()
    except (requests.RequestException, ValueError):
        # В адресе запроса есть ключ, поэтому исключение requests не выводим
        raise FlightServiceError("Сервис статусов рейсов сейчас недоступен, попробуйте позже") from None

    if not isinstance(payload, dict):
        raise FlightServiceError("Сервис вернул некорректный ответ")
    error = payload.get("error")
    if error or not response.ok:
        code = error.get("code") if isinstance(error, dict) else None
        messages = {
            "invalid_access_key": "Сервис не принял API-ключ",
            "missing_access_key": "Ключ сервиса статусов рейсов не настроен",
            "inactive_user": "Аккаунт авиа-API не активирован",
            "usage_limit_reached": "Лимит запросов Aviationstack исчерпан",
            "rate_limit_reached": "Лимит запросов Aviationstack достигнут",
            "function_access_restricted": "Тариф Aviationstack не поддерживает этот запрос",
            "https_access_restricted": "Тариф Aviationstack не поддерживает защищённое подключение",
        }
        raise FlightServiceError(messages.get(code, "Aviationstack отклонил запрос, попробуйте позже"))
    flights = payload.get("data")
    if not isinstance(flights, list):
        raise FlightServiceError("Сервис вернул некорректный список рейсов")
    flight = _pick_closest_flight(flights, transport)
    return _extract_status_and_time(flight) if flight else None
