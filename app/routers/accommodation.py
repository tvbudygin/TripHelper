from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.accommodation import Accommodation
from app.models.user import User
from app.schemas.accommodation import AccommodationCreate, AccommodationOut, AccommodationUpdate
from app.routers.auth import get_current_user
from app.services.trip_service import get_owned_trip

router = APIRouter(prefix="/trips/{trip_id}/accommodations", tags=["accommodations"])


@router.get("/", response_model=list[AccommodationOut])
def list_accommodations(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Список жилья поездки"""

    get_owned_trip(db, trip_id, current_user.id)
    return (
        db.query(Accommodation)
        .filter(Accommodation.trip_id == trip_id)
        .order_by(Accommodation.check_in_date)
        .all()
    )


@router.post("/", response_model=AccommodationOut, status_code=status.HTTP_201_CREATED)
def create_accommodation(
    trip_id: str,
    data: AccommodationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавление жилья"""

    get_owned_trip(db, trip_id, current_user.id)
    if data.check_in_date and data.check_out_date and data.check_out_date < data.check_in_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата выезда не может быть раньше даты заселения",
        )

    new_accommodation = Accommodation(trip_id=trip_id, **data.model_dump())
    db.add(new_accommodation)
    db.commit()
    db.refresh(new_accommodation)
    return new_accommodation


@router.patch("/{accommodation_id}", response_model=AccommodationOut)
def update_accommodation(
    trip_id: str,
    accommodation_id: str,
    data: AccommodationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Изменение жилья"""

    get_owned_trip(db, trip_id, current_user.id)
    accommodation = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id, Accommodation.trip_id == trip_id
    ).first()
    if not accommodation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Жильё не найдено")

    updates = data.model_dump(exclude_unset=True)
    new_check_in = updates.get("check_in_date", accommodation.check_in_date)
    new_check_out = updates.get("check_out_date", accommodation.check_out_date)
    if new_check_in and new_check_out and new_check_out < new_check_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата выезда не может быть раньше даты заселения",
        )

    for field, value in updates.items():
        setattr(accommodation, field, value)

    db.commit()
    db.refresh(accommodation)
    return accommodation


@router.delete("/{accommodation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accommodation(
    trip_id: str,
    accommodation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаление жилья"""

    get_owned_trip(db, trip_id, current_user.id)
    found = db.query(Accommodation).filter(
        Accommodation.id == accommodation_id, Accommodation.trip_id == trip_id
    ).first()
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Жильё не найдено")
    db.delete(found)
    db.commit()
