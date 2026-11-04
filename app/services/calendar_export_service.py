"""Создание файла календаря (.ics) для поездки"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.models.trip import Trip


def _escape(text: str) -> str:
    """Экранирует спецсимволы для .ics"""

    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def _format_datetime(value: datetime) -> str:
    """Дата и время в формате .ics"""

    return value.strftime("%Y%m%dT%H%M%S")


def _format_date(value: date) -> str:
    """Дата в формате .ics"""

    return value.strftime("%Y%m%d")


def _time_or_all_day(day: date, time_text: str | None) -> tuple[str, str]:
    """Начало и конец события: на час, если есть время, иначе на весь день"""

    if time_text:
        try:
            start = datetime.combine(day, datetime.strptime(time_text, "%H:%M").time())
            return f"DTSTART:{_format_datetime(start)}", f"DTEND:{_format_datetime(start + timedelta(hours=1))}"
        except ValueError:
            pass
    return (
        f"DTSTART;VALUE=DATE:{_format_date(day)}",
        f"DTEND;VALUE=DATE:{_format_date(day + timedelta(days=1))}",
    )


def _event(uid: str, summary: str, start_line: str, end_line: str, description: str = "") -> list[str]:
    """Собирает одно событие календаря"""

    lines = [
        "BEGIN:VEVENT",
        f"UID:{uid}@triphelper",
        f"DTSTAMP:{_format_datetime(datetime.utcnow())}Z",
        f"SUMMARY:{_escape(summary)}",
        start_line,
        end_line,
    ]
    if description:
        lines.append(f"DESCRIPTION:{_escape(description)}")
    lines.append("END:VEVENT")
    return lines


def _trip_events(trip: Trip) -> list[str]:
    """События одной поездки: сама поездка, перемещения, жильё и активности"""

    lines = _event(
        uid=f"trip-{trip.id}",
        summary=f"Поездка: {trip.title}",
        start_line=f"DTSTART;VALUE=DATE:{_format_date(trip.start_date)}",
        end_line=f"DTEND;VALUE=DATE:{_format_date(trip.end_date + timedelta(days=1))}",
        description=f"{trip.city}, {trip.country}",
    )

    for transport in trip.transports:
        if not transport.departure_datetime:
            continue
        start = transport.actual_departure_datetime or transport.departure_datetime
        end = transport.arrival_datetime or (start + timedelta(hours=2))
        route = f"{transport.departure_location or '?'} → {transport.arrival_location or '?'}"
        details = [
            transport.airline,
            transport.ticket_number,
            f"вагон {transport.carriage}" if transport.carriage else None,
            f"место {transport.seat}" if transport.seat else None,
            transport.gate_or_platform,
        ]
        lines += _event(
            uid=f"transport-{transport.id}",
            summary=f"{transport.type}: {route}",
            start_line=f"DTSTART:{_format_datetime(start)}",
            end_line=f"DTEND:{_format_datetime(end)}",
            description=", ".join(part for part in details if part),
        )

    for accommodation in trip.accommodations:
        name = accommodation.name or accommodation.type
        if accommodation.check_in_date:
            start_line, end_line = _time_or_all_day(accommodation.check_in_date, accommodation.check_in_time)
            lines += _event(
                uid=f"checkin-{accommodation.id}",
                summary=f"Заселение: {name}",
                start_line=start_line,
                end_line=end_line,
                description=accommodation.address or "",
            )
        if accommodation.check_out_date:
            start_line, end_line = _time_or_all_day(accommodation.check_out_date, accommodation.check_out_time)
            lines += _event(
                uid=f"checkout-{accommodation.id}",
                summary=f"Выезд: {name}",
                start_line=start_line,
                end_line=end_line,
            )

    for activity in trip.activities:
        if not activity.visit_date:
            continue
        start_line, end_line = _time_or_all_day(activity.visit_date, activity.visit_time or activity.opening_time)
        working_hours = ""
        if activity.opening_time and activity.closing_time:
            working_hours = f"Работает {activity.opening_time}–{activity.closing_time}"
        lines += _event(
            uid=f"activity-{activity.id}",
            summary=f"{activity.type}: {activity.title or 'без названия'}",
            start_line=start_line,
            end_line=end_line,
            description=", ".join(part for part in (working_hours, activity.address) if part),
        )

    return lines


def build_ics(trips: list[Trip], time_zone: str = "Europe/Moscow") -> str:
    """Собирает календарь из всех поездок"""

    zone = ZoneInfo(time_zone)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//TripHelper//RU", "CALSCALE:GREGORIAN"]
    for trip in trips:
        lines += _trip_events(trip)
    # Записываем время в UTC, чтобы календарь не выбирал случайный часовой пояс
    for index, line in enumerate(lines):
        if line.startswith(("DTSTART:", "DTEND:")):
            field, value = line.split(":", 1)
            local_time = datetime.strptime(value, "%Y%m%dT%H%M%S").replace(tzinfo=zone)
            utc_time = local_time.astimezone(timezone.utc)
            lines[index] = f"{field}:{_format_datetime(utc_time)}Z"
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
