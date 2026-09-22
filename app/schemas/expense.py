from datetime import datetime
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    """Данные для добавления расхода"""

    title: str
    amount: float
    category: str | None = None


class ExpenseOut(BaseModel):
    """Расход для фронтенда"""

    id: str
    trip_id: str
    title: str
    amount: float
    category: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
