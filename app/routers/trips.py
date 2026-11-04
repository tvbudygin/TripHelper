from datetime import date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.notification import Notification
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripOut, TripDetailOut, TripUpdate
from app.routers.auth import get_current_user
from app.services.calendar_export_service import build_ics
from app.services.notification_service import forget_reminder
from app.services.trip_service import complete_finished_trips, get_owned_trip

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/", response_model=list[TripOut])
def list_trips(today: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Список поездок пользователя; today - сегодняшняя дата на его устройстве"""

    complete_finished_trips(db, current_user.id, today)
    return db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()


@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(data: TripCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Создание поездки"""

    if data.end_date < data.start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Дата окончания не может быть раньше начала")

    new_trip = Trip(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        country=data.country,
        extra_stops=[stop.model_dump() for stop in data.extra_stops],
        origin_country=data.origin_country,
        city=data.city,
        start_date=data.start_date,
        end_date=data.end_date,
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip


@router.get("/export.ics")
def export_calendar(time_zone: str = "Europe/Moscow", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Скачать все поездки как файл календаря .ics"""

    try:
        ZoneInfo(time_zone)
    except (ZoneInfoNotFoundError, ValueError):
        raise HTTPException(status_code=400, detail="Неизвестный часовой пояс") from None
    trips = db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.start_date).all()
    return Response(
        content=build_ics(trips, time_zone),
        media_type="text/calendar",
        headers={"Content-Disposition": 'attachment; filename="TripHelper.ics"'},
    )


@router.get("/{trip_id}", response_model=TripDetailOut)
def get_trip(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Поездка со всеми перемещениями, жильём, активностями и расходами"""

    return get_owned_trip(db, trip_id, current_user.id)


@router.patch("/{trip_id}", response_model=TripOut)
def update_trip(
    trip_id: str,
    data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Изменение поездки"""

    trip = get_owned_trip(db, trip_id, current_user.id)
    updates = data.model_dump(exclude_unset=True)

    new_start = updates.get("start_date", trip.start_date)
    new_end = updates.get("end_date", trip.end_date)
    if new_end < new_start:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Дата окончания не может быть раньше начала")

    if any(field in updates and updates[field] != getattr(trip, field) for field in ("title", "start_date")):
        forget_reminder(db, "trip_upcoming", trip.id)

    for field, value in updates.items():
        setattr(trip, field, value)

    # если поездку вернули из завершённых, автоматически её больше не завершаем
    if updates.get("is_completed") is False:
        trip.auto_complete_blocked = True

    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Удаление поездки"""

    found = get_owned_trip(db, trip_id, current_user.id)
    # уведомления ссылаются на поездку, поэтому удаляем их вместе с ней
    db.query(Notification).filter(Notification.trip_id == trip_id).delete()
    db.delete(found)
    db.commit()
