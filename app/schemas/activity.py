from datetime import date
from pydantic import BaseModel


class ActivityCreate(BaseModel):
    """Данные для добавления активности"""

    type: str
    title: str | None = None
    visit_date: date | None = None
    visit_time: str | None = None
    opening_time: str | None = None
    closing_time: str | None = None
    address: str | None = None
    price: float | None = None
    document_url: str | None = None
    notes: str | None = None


class ActivityUpdate(BaseModel):
    """Данные для изменения активности"""

    type: str | None = None
    title: str | None = None
    visit_date: date | None = None
    visit_time: str | None = None
    opening_time: str | None = None
    closing_time: str | None = None
    address: str | None = None
    price: float | None = None
    document_url: str | None = None
    notes: str | None = None


class ActivityOut(BaseModel):
    """Активность для фронтенда"""

    id: str
    trip_id: str
    type: str
    title: str | None = None
    visit_date: date | None = None
    visit_time: str | None = None
    opening_time: str | None = None
    closing_time: str | None = None
    address: str | None = None
    price: float | None = None
    document_url: str | None = None
    notes: str | None = None

    class Config:
        from_attributes = True
