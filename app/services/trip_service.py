from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.trip import Trip


def get_owned_trip(db: Session, trip_id: str, user_id: str) -> Trip:
    """Находит поездку пользователя или отдаёт 404"""

    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Поездка не найдена")
    return trip


def complete_finished_trips(db: Session, user_id: str | None = None) -> None:
    """Завершает поездки, у которых прошла дата окончания (кроме тех, что пользователь вернул сам)"""

    query = db.query(Trip).filter(
        Trip.end_date < date.today(),
        Trip.is_completed.is_(False),
        Trip.auto_complete_blocked.is_(False),
    )
    if user_id:
        query = query.filter(Trip.user_id == user_id)
    for trip in query.all():
        trip.is_completed = True
    db.commit()
