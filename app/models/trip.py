import uuid
from datetime import datetime, date

from sqlalchemy import JSON, Boolean, String, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Trip(Base):
    """Таблица поездок"""

    __tablename__ = "trips"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    # другие страны поездки: [{"country": "Франция", "city": "Париж"}]
    extra_stops: Mapped[list] = mapped_column(JSON, default=list, server_default="[]", nullable=False)
    # страна выезда (для карты)
    origin_country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    # True, если пользователь вернул поездку из завершённых (тогда автоматически не завершаем)
    auto_complete_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)

    user: Mapped["User"] = relationship(back_populates="trips")
    transports: Mapped[list["Transport"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    accommodations: Mapped[list["Accommodation"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    activities: Mapped[list["Activity"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    expenses: Mapped[list["Expense"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
