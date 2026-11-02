from datetime import datetime
from pydantic import BaseModel


class TransportCreate(BaseModel):
    """Данные для добавления перемещения"""

    type: str
    departure_location: str | None = None
    arrival_location: str | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    departure_datetime: datetime | None = None
    arrival_datetime: datetime | None = None
    price: float | None = None
    ticket_number: str | None = None
    airline: str | None = None
    gate_or_platform: str | None = None
    carriage: str | None = None
    seat: str | None = None
    document_url: str | None = None
    notes: str | None = None


class TransportUpdate(BaseModel):
    """Данные для изменения перемещения"""

    type: str | None = None
    departure_location: str | None = None
    arrival_location: str | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    departure_datetime: datetime | None = None
    arrival_datetime: datetime | None = None
    price: float | None = None
    ticket_number: str | None = None
    airline: str | None = None
    gate_or_platform: str | None = None
    carriage: str | None = None
    seat: str | None = None
    status: str | None = None
    document_url: str | None = None
    notes: str | None = None


class TransportOut(BaseModel):
    """Перемещение для фронтенда"""

    id: str
    trip_id: str
    type: str
    departure_location: str | None = None
    arrival_location: str | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    departure_datetime: datetime | None = None
    arrival_datetime: datetime | None = None
    price: float | None = None
    ticket_number: str | None = None
    airline: str | None = None
    gate_or_platform: str | None = None
    carriage: str | None = None
    seat: str | None = None
    status: str
    actual_departure_datetime: datetime | None = None
    flight_summary: str | None = None
    document_url: str | None = None
    notes: str | None = None

    class Config:
        from_attributes = True
