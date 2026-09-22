from pydantic import BaseModel


class StatsOut(BaseModel):
    """Статистика профиля"""

    total_trips: int
    countries_visited: int
    cities_visited: int
    total_activities: int
    total_transports: int
    total_accommodations: int
