import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Transport(Base):
    """Таблица перемещений — самолёты, поезда, автобусы и тд."""

    __tablename__ = "transports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    departure_location: Mapped[str] = mapped_column(String(200), nullable=False)
    arrival_location: Mapped[str] = mapped_column(String(200), nullable=False)
    departure_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    arrival_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ticket_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    trip: Mapped["Trip"] = relationship(back_populates="transports")
