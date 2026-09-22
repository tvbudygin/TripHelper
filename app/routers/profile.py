from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserOut, UserSettingsUpdate
from app.schemas.stats import StatsOut
from app.services.stats_service import get_user_stats, get_visited_countries
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """Данные профиля"""

    return current_user


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Статистика путешествий"""

    return get_user_stats(db, current_user.id)


@router.get("/visited-countries", response_model=list[str])
def visited_countries(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Страны для карты путешествий"""

    return get_visited_countries(db, current_user.id)


@router.patch("/settings", response_model=UserOut)
def update_settings(
    data: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Включение и выключение уведомлений"""

    current_user.notifications_enabled = data.notifications_enabled
    db.commit()
    db.refresh(current_user)
    return current_user
