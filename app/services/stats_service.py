from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Trip, Activity, Transport, Accommodation
from app.models.user_stats import UserStats
from app.schemas.stats import StatsOut


def get_visited_countries(db: Session, user_id: str) -> list[str]:
    """Страны, где был пользователь: страна поездки, другие страны маршрута и страна выезда"""

    names = []
    trip_rows = db.query(Trip.country, Trip.extra_stops, Trip.origin_country).filter(Trip.user_id == user_id).all()
    for country, extra_stops, origin_country in trip_rows:
        names += [country, origin_country]
        names += [stop.get("country") for stop in extra_stops or []]
    unique: dict[str, str] = {}
    for name in names:
        cleaned = (name or "").strip()
        if cleaned:
            unique.setdefault(cleaned.lower(), cleaned)
    return list(unique.values())


def get_user_stats(db: Session, user_id: str) -> StatsOut:
    """Считает статистику пользователя и сохраняет её в таблицу"""

    trip_count = db.query(func.count(Trip.id)).filter(Trip.user_id == user_id).scalar() or 0
    country_count = len(get_visited_countries(db, user_id))
    city_count = db.query(func.count(func.distinct(Trip.city))).filter(Trip.user_id == user_id).scalar() or 0
    act_count = db.query(func.count(Activity.id)).join(Trip).filter(Trip.user_id == user_id).scalar() or 0
    tr_count = db.query(func.count(Transport.id)).join(Trip).filter(Trip.user_id == user_id).scalar() or 0
    acc_count = db.query(func.count(Accommodation.id)).join(Trip).filter(Trip.user_id == user_id).scalar() or 0

    result = StatsOut(
        total_trips=trip_count,
        countries_visited=country_count,
        cities_visited=city_count,
        total_activities=act_count,
        total_transports=tr_count,
        total_accommodations=acc_count,
    )

    row = db.query(UserStats).filter(UserStats.user_id == user_id).first()
    if row:
        row.total_trips = trip_count
        row.countries_visited = country_count
        row.cities_visited = city_count
        row.total_activities = act_count
        row.total_transports = tr_count
        row.total_accommodations = acc_count
    else:
        db.add(UserStats(
            user_id=user_id,
            total_trips=trip_count,
            countries_visited=country_count,
            cities_visited=city_count,
            total_activities=act_count,
            total_transports=tr_count,
            total_accommodations=acc_count,
        ))

    db.commit()
    return result
