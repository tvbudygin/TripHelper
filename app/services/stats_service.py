from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Trip, Activity, Transport, Accommodation
from app.models.user_stats import UserStats
from app.schemas.stats import StatsOut


def get_user_stats(db: Session, user_id: str) -> StatsOut:
    """Собираю статистику юзера — сколько поездок, стран, городов и тд. Результат кэшу в таблицу."""

    trip_count = db.query(func.count(Trip.id)).filter(Trip.user_id == user_id).scalar() or 0
    country_count = db.query(func.count(func.distinct(Trip.country))).filter(Trip.user_id == user_id).scalar() or 0
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
