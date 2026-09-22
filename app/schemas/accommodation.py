from datetime import date
from pydantic import BaseModel


class AccommodationCreate(BaseModel):
    """Данные для добавления жилья"""

    name: str | None = None
    type: str
    address: str | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    check_in_time: str | None = None
    check_out_time: str | None = None
    price: float | None = None
    document_url: str | None = None
    notes: str | None = None


class AccommodationUpdate(BaseModel):
    """Данные для изменения жилья"""

    name: str | None = None
    type: str | None = None
    address: str | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    check_in_time: str | None = None
    check_out_time: str | None = None
    price: float | None = None
    document_url: str | None = None
    notes: str | None = None


class AccommodationOut(BaseModel):
    """Жильё для фронтенда"""

    id: str
    trip_id: str
    name: str | None = None
    type: str
    address: str | None = None
    check_in_date: date | None = None
    check_out_date: date | None = None
    check_in_time: str | None = None
    check_out_time: str | None = None
    price: float | None = None
    document_url: str | None = None
    notes: str | None = None

    class Config:
        from_attributes = True
