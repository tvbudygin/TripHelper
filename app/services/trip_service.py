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


def complete_finished_trips(db: Session, user_id: str, today: date) -> None:
    """Завершает поездки пользователя, у которых прошла дата окончания (кроме тех, что он вернул сам)"""

    finished_trips = db.query(Trip).filter(
        Trip.user_id == user_id,
        Trip.end_date < today,
        Trip.is_completed.is_(False),
        Trip.auto_complete_blocked.is_(False),
    )
    for trip in finished_trips:
        trip.is_completed = True
    db.commit()
