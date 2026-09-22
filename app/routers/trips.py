from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripOut, TripDetailOut, TripUpdate
from app.routers.auth import get_current_user
from app.services.calendar_export_service import build_ics
from app.services.trip_service import complete_finished_trips, get_owned_trip

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/", response_model=list[TripOut])
def list_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Список поездок пользователя"""

    complete_finished_trips(db, current_user.id)
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
        status="planning",
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip


@router.get("/{trip_id}", response_model=TripDetailOut)
def get_trip(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Поездка со всеми перемещениями, жильём, активностями и расходами"""

    complete_finished_trips(db, current_user.id)
    trip = (
        db.query(Trip)
        .options(
            joinedload(Trip.transports),
            joinedload(Trip.accommodations),
            joinedload(Trip.activities),
            joinedload(Trip.expenses),
        )
        .filter(Trip.id == trip_id, Trip.user_id == current_user.id)
        .first()
    )
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Поездка не найдена")
    return trip


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

    for field, value in updates.items():
        setattr(trip, field, value)

    # если поездку вернули из завершённых, автоматически её больше не завершаем
    if updates.get("is_completed") is False:
        trip.auto_complete_blocked = True

    db.commit()
    db.refresh(trip)
    return trip


@router.get("/{trip_id}/export.ics")
def export_trip_calendar(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Скачать поездку как файл календаря .ics"""

    trip = get_owned_trip(db, trip_id, current_user.id)
    return Response(
        content=build_ics(trip),
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(trip.title)}.ics"},
    )


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Удаление поездки"""

    found = get_owned_trip(db, trip_id, current_user.id)
    db.delete(found)
    db.commit()
