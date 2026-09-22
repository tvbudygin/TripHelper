import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Transport(Base):
    """Таблица перемещений — самолёты, поезда, автобусы и тд"""

    __tablename__ = "transports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trip_id: Mapped[str] = mapped_column(ForeignKey("trips.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    departure_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    arrival_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    departure_airport: Mapped[str | None] = mapped_column(String(100), nullable=True)
    arrival_airport: Mapped[str | None] = mapped_column(String(100), nullable=True)
    departure_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    arrival_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    ticket_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    airline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # гейт, платформа или пирс — зависит от вида транспорта
    carriage: Mapped[str | None] = mapped_column(String(20), nullable=True)
    seat: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gate_or_platform: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    # новое время вылета, если рейс задержали
    actual_departure_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    trip: Mapped["Trip"] = relationship(back_populates="transports")
