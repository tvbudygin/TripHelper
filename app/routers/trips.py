from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripOut
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("/", response_model=list[TripOut])
def list_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Показываю все поездки юзера, новые сверху."""

    return db.query(Trip).filter(Trip.user_id == current_user.id).order_by(Trip.created_at.desc()).all()


@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
def create_trip(data: TripCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Добавляю новую поездку в базу, привязываю к юзеру."""

    if data.end_date < data.start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Дата окончания не может быть раньше начала")

    new_trip = Trip(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        country=data.country,
        city=data.city,
        start_date=data.start_date,
        end_date=data.end_date,
        status="planning",
    )
    db.add(new_trip)
    db.commit()
    db.refresh(new_trip)
    return new_trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Удаляю поездку, но только если она принадлежит этому юзеру."""

    found = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == current_user.id).first()
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Поездка не найдена")
    db.delete(found)
    db.commit()
