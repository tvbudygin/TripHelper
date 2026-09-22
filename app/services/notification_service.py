from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.models.transport import Transport
from app.models.notification import Notification
from app.models.user import User
from app.services.email_service import send_email

UPCOMING_TRIP_DAYS = 3
UPCOMING_TRANSPORT_HOURS = 24
RETRY_EMAIL_DAYS = 2


def notify(db: Session, user: User, trip_id: str, entity_id: str, category: str, title: str, message: str) -> None:
    """Создаёт уведомление и отправляет копию на почту, если уведомления включены"""

    email_sent = send_email(user.email, title, message) if user.notifications_enabled else True
    db.add(Notification(
        user_id=user.id,
        trip_id=trip_id,
        entity_id=entity_id,
        category=category,
        title=title,
        message=message,
        email_sent=email_sent,
    ))


def _already_notified(db: Session, user_id: str, category: str, entity_id: str) -> bool:
    """Проверяет, было ли уже такое уведомление"""

    existing = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.category == category,
        Notification.entity_id == entity_id,
    ).first()
    return existing is not None


def generate_upcoming_notifications(db: Session, user: User) -> None:
    """Создаёт напоминания о скорых поездках и отправлениях пользователя"""

    if not user.notifications_enabled:
        return

    user_id = user.id
    now = datetime.utcnow()
    today = now.date()
    trip_deadline = today + timedelta(days=UPCOMING_TRIP_DAYS)

    upcoming_trips = (
        db.query(Trip)
        .filter(Trip.user_id == user_id, Trip.start_date >= today, Trip.start_date <= trip_deadline)
        .all()
    )
    for trip in upcoming_trips:
        if not _already_notified(db, user_id, "trip_upcoming", trip.id):
            notify(
                db, user, trip.id, trip.id, "trip_upcoming",
                "Скоро поездка",
                f"Поездка «{trip.title}» начинается {trip.start_date.strftime('%d.%m.%Y')}.",
            )

    transport_deadline = now + timedelta(hours=UPCOMING_TRANSPORT_HOURS)
    upcoming_transports = (
        db.query(Transport)
        .join(Trip)
        .filter(
            Trip.user_id == user_id,
            Transport.departure_datetime >= now,
            Transport.departure_datetime <= transport_deadline,
        )
        .all()
    )
    for transport in upcoming_transports:
        if not _already_notified(db, user_id, "transport_upcoming", transport.id):
            departs_at = transport.departure_datetime.strftime("%d.%m.%Y %H:%M")
            notify(
                db, user, transport.trip_id, transport.id, "transport_upcoming",
                "Скоро отправление",
                f"{transport.departure_location} → {transport.arrival_location}, {departs_at}.",
            )

    db.commit()


def retry_unsent_emails(db: Session) -> None:
    """Повторно отправляет письма, которые не ушли с первого раза"""

    since = datetime.utcnow() - timedelta(days=RETRY_EMAIL_DAYS)
    unsent = (
        db.query(Notification)
        .filter(
            Notification.email_sent.is_(False),
            Notification.is_deleted.is_(False),
            Notification.created_at >= since,
        )
        .all()
    )
    for notification in unsent:
        user = db.get(User, notification.user_id)
        if user and user.notifications_enabled and send_email(user.email, notification.title, notification.message):
            notification.email_sent = True
    db.commit()


def generate_notifications_for_all_users(db: Session) -> None:
    """Создаёт напоминания для всех пользователей (вызывается из фоновой проверки)"""

    for user in db.query(User).filter(User.notifications_enabled.is_(True)).all():
        try:
            generate_upcoming_notifications(db, user)
        except Exception as error:
            db.rollback()
            print(f"[TripHelper] Не удалось создать напоминания для {user.email}: {error}")
    retry_unsent_emails(db)
