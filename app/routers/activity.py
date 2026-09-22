from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.activity import Activity
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityOut, ActivityUpdate
from app.routers.auth import get_current_user
from app.services.trip_service import get_owned_trip

router = APIRouter(prefix="/trips/{trip_id}/activities", tags=["activities"])


@router.get("/", response_model=list[ActivityOut])
def list_activities(trip_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Показываю все активности поездки (музеи, экскурсии и тд), по дате посещения"""

    get_owned_trip(db, trip_id, current_user.id)
    return (
        db.query(Activity)
        .filter(Activity.trip_id == trip_id)
        .order_by(Activity.visit_date)
        .all()
    )


@router.post("/", response_model=ActivityOut, status_code=status.HTTP_201_CREATED)
def create_activity(
    trip_id: str,
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавляю новую активность (место, событие) в поездку"""

    get_owned_trip(db, trip_id, current_user.id)
    new_activity = Activity(trip_id=trip_id, **data.model_dump())
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


@router.patch("/{activity_id}", response_model=ActivityOut)
def update_activity(
    trip_id: str,
    activity_id: str,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Меняю данные активности — присылают только те поля, которые редактировали"""

    get_owned_trip(db, trip_id, current_user.id)
    activity = db.query(Activity).filter(Activity.id == activity_id, Activity.trip_id == trip_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Активность не найдена")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    trip_id: str,
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаляю активность, если она относится к поездке этого юзера"""

    get_owned_trip(db, trip_id, current_user.id)
    found = db.query(Activity).filter(Activity.id == activity_id, Activity.trip_id == trip_id).first()
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Активность не найдена")
    db.delete(found)
    db.commit()
