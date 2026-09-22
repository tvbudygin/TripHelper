"""Ответ на сообщение чата: классификатор, агент и валидатор"""

from datetime import date

from sqlalchemy.orm import Session

from app.ai.agent import generate_answer
from app.ai.classifier import classify_question
from app.ai.validator import validate_answer
from app.models.accommodation import Accommodation
from app.models.activity import Activity
from app.models.transport import Transport
from app.models.trip import Trip

OFF_TOPIC_ANSWER = "Я помогаю только с вопросами о путешествиях — задайте что-то про вашу поездку."
UNAVAILABLE_ANSWER = "Не могу сейчас дать точный ответ — ИИ-помощник временно недоступен. Попробуйте позже."


def _find_relevant_trip(db: Session, user_id: str) -> Trip | None:
    """Находит поездку, о которой спрашивают: текущую, если нет то ближайшую, если не то последнюю"""

    today = date.today()

    ongoing = (
        db.query(Trip)
        .filter(Trip.user_id == user_id, Trip.start_date <= today, Trip.end_date >= today)
        .first()
    )
    if ongoing:
        return ongoing

    upcoming = (
        db.query(Trip)
        .filter(Trip.user_id == user_id, Trip.start_date > today)
        .order_by(Trip.start_date)
        .first()
    )
    if upcoming:
        return upcoming

    return db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.start_date.desc()).first()


def _build_trip_context(db: Session, user_id: str) -> str:
    """Собирает данные о нужной поездке для агента"""

    trip = _find_relevant_trip(db, user_id)
    if not trip:
        return "У пользователя пока нет ни одной поездки в системе."

    lines = [f"Поездка «{trip.title}»: город {trip.city}, страна {trip.country}, с {trip.start_date} по {trip.end_date}."]
    for stop in trip.extra_stops or []:
        lines.append(f"Также в поездке: {stop.get('city') or 'город не указан'}, {stop.get('country')}.")
    if trip.origin_country:
        lines.append(f"Выезд из страны: {trip.origin_country}.")
    if trip.description:
        lines.append(f"Заметки к поездке: {trip.description}")

    transports = (
        db.query(Transport)
        .filter(Transport.trip_id == trip.id)
        .order_by(Transport.departure_datetime)
        .all()
    )
    for transport in transports:
        line = (
            f"Перемещение: {transport.type}, {transport.departure_location} → "
            f"{transport.arrival_location}, вылет: {transport.departure_datetime}, статус: {transport.status}."
        )
        if transport.price is not None:
            line += f" Стоимость: {transport.price}."
        if transport.arrival_datetime:
            line += f" Прибытие: {transport.arrival_datetime}."
        if transport.airline:
            line += f" Авиакомпания: {transport.airline}."
        if transport.ticket_number:
            line += f" Номер рейса/билета: {transport.ticket_number}."
        if transport.departure_airport or transport.arrival_airport:
            line += f" Аэропорты: {transport.departure_airport or '?'} → {transport.arrival_airport or '?'}."
        if transport.carriage:
            line += f" Вагон: {transport.carriage}."
        if transport.seat:
            line += f" Место: {transport.seat}."
        if transport.gate_or_platform:
            line += f" Гейт/платформа: {transport.gate_or_platform}."
        if transport.actual_departure_datetime:
            line += f" Новое время вылета: {transport.actual_departure_datetime}."
        if transport.notes:
            line += f" Заметки: {transport.notes}."
        lines.append(line)

    accommodations = db.query(Accommodation).filter(Accommodation.trip_id == trip.id).all()
    for accommodation in accommodations:
        line = (
            f"Жильё: {accommodation.name} ({accommodation.type}), "
            f"с {accommodation.check_in_date} по {accommodation.check_out_date}."
        )
        if accommodation.check_in_time or accommodation.check_out_time:
            line += (
                f" Время заселения: {accommodation.check_in_time or 'не указано'},"
                f" время выезда: {accommodation.check_out_time or 'не указано'}."
            )
        if accommodation.address:
            line += f" Адрес: {accommodation.address}."
        if accommodation.notes:
            line += f" Заметки: {accommodation.notes}."
        lines.append(line)

    activities = (
        db.query(Activity).filter(Activity.trip_id == trip.id).order_by(Activity.visit_date).all()
    )
    for activity in activities:
        line = f"Активность: {activity.title} ({activity.type}), дата: {activity.visit_date}."
        if activity.visit_time:
            line += f" Время посещения: {activity.visit_time}."
        if activity.opening_time or activity.closing_time:
            line += f" Работает с {activity.opening_time or '?'} до {activity.closing_time or '?'}."
        if activity.address:
            line += f" Адрес: {activity.address}."
        if activity.notes:
            line += f" Заметки: {activity.notes}."
        lines.append(line)

    return "\n".join(lines)


def answer_message(db: Session, user_id: str, question: str, history: list[dict] | None = None) -> str:
    """Отвечает на сообщение пользователя"""

    category = classify_question(question, history)
    if category == "off_topic":
        return OFF_TOPIC_ANSWER

    trip_context = _build_trip_context(db, user_id)
    draft_answer = generate_answer(question, trip_context, history)
    if not draft_answer:
        return UNAVAILABLE_ANSWER

    if category != "trip_info":
        draft_answer = validate_answer(question, trip_context, draft_answer)

    return draft_answer
