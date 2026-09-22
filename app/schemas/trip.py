from datetime import date, datetime
from pydantic import BaseModel

from app.schemas.transport import TransportOut
from app.schemas.accommodation import AccommodationOut
from app.schemas.activity import ActivityOut
from app.schemas.expense import ExpenseOut


class TripStop(BaseModel):
    """Дополнительная страна поездки и город в ней"""

    country: str
    city: str | None = None


class TripCreate(BaseModel):
    """Данные для создания поездки"""

    title: str
    description: str | None = None
    country: str
    city: str
    extra_stops: list[TripStop] = []
    origin_country: str | None = None
    start_date: date
    end_date: date


class TripUpdate(BaseModel):
    """Данные для изменения поездки"""

    title: str | None = None
    description: str | None = None
    country: str | None = None
    extra_stops: list[TripStop] | None = None
    origin_country: str | None = None
    city: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_completed: bool | None = None


class TripOut(BaseModel):
    """Поездка для фронтенда"""

    id: str
    user_id: str
    title: str
    description: str | None = None
    country: str
    city: str
    extra_stops: list[TripStop] = []
    origin_country: str | None = None
    start_date: date
    end_date: date
    status: str
    is_completed: bool
    cover_image_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class TripDetailOut(TripOut):
    """Поездка вместе с перемещениями, жильём, активностями и расходами"""

    transports: list[TransportOut] = []
    accommodations: list[AccommodationOut] = []
    activities: list[ActivityOut] = []
    expenses: list[ExpenseOut] = []
