import uuid
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserStats(Base):
    """Таблица статистики — чтобы быстро показывать цифры в профиле без пересчёта."""

    __tablename__ = "user_stats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True, index=True)
    total_trips: Mapped[int] = mapped_column(Integer, default=0)
    countries_visited: Mapped[int] = mapped_column(Integer, default=0)
    cities_visited: Mapped[int] = mapped_column(Integer, default=0)
    total_activities: Mapped[int] = mapped_column(Integer, default=0)
    total_transports: Mapped[int] = mapped_column(Integer, default=0)
    total_accommodations: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="stats")
