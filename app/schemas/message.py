from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    """Сообщение пользователя"""

    content: str


class MessageOut(BaseModel):
    """Сообщение чата для фронтенда"""

    id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
