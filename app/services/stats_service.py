from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Trip, Activity, Transport, Accommodation
from app.schemas.stats import StatsOut


def get_visited_countries(db: Session, user_id: str) -> list[str]:
    """Страны, где был пользователь: страна поездки, другие страны маршрута и страна выезда"""

    names = []
    trip_rows = db.query(Trip.country, Trip.extra_stops, Trip.origin_country).filter(Trip.user_id == user_id).all()
    for country, extra_stops, origin_country in trip_rows:
        names += [country, origin_country]
        names += [stop.get("country") for stop in extra_stops]
    unique: dict[str, str] = {}
    for name in names:
        cleaned = (name or "").strip()
        if cleaned:
            unique.setdefault(cleaned.lower(), cleaned)
    return list(unique.values())


def get_user_stats(db: Session, user_id: str) -> StatsOut:
    """Считает статистику пользователя"""

    return StatsOut(
        total_trips=db.query(func.count(Trip.id)).filter(Trip.user_id == user_id).scalar(),
        countries_visited=len(get_visited_countries(db, user_id)),
        cities_visited=db.query(func.count(func.distinct(Trip.city))).filter(Trip.user_id == user_id).scalar(),
        total_activities=db.query(func.count(Activity.id)).join(Trip).filter(Trip.user_id == user_id).scalar(),
        total_transports=db.query(func.count(Transport.id)).join(Trip).filter(Trip.user_id == user_id).scalar(),
        total_accommodations=db.query(func.count(Accommodation.id)).join(Trip).filter(Trip.user_id == user_id).scalar(),
    )
