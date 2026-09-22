from datetime import datetime
from pydantic import BaseModel


class NotificationOut(BaseModel):
    """Уведомление для фронтенда"""

    id: str
    trip_id: str | None = None
    entity_id: str | None = None
    category: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
