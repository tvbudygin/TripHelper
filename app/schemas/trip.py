from datetime import date, datetime
from pydantic import BaseModel


class TripCreate(BaseModel):
    """Что юзер заполняет в форме создания поездки."""

    title: str
    description: str | None = None
    country: str
    city: str
    start_date: date
    end_date: date


class TripOut(BaseModel):
    """Что отдаю фронтенду про поездку."""

    id: str
    user_id: str
    title: str
    description: str | None = None
    country: str
    city: str
    start_date: date
    end_date: date
    status: str
    cover_image_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
