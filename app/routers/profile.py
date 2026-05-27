from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserOut
from app.schemas.stats import StatsOut
from app.services.stats_service import get_user_stats
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """Отдаю инфу профиля — имя, почта, аватар."""

    return current_user


@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Считаю и отдаю статистику — сколько стран, городов, поездок и тд."""

    return get_user_stats(db, current_user.id)
