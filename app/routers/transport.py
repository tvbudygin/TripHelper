from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.transport import Transport
from app.models.user import User
from app.schemas.transport import TransportCreate, TransportOut, TransportUpdate
from app.routers.auth import get_current_user
from app.services.flight_status_service import FlightServiceError, fetch_real_status
from app.services.notification_service import forget_reminder, notify
from app.services.trip_service import get_owned_trip

router = APIRouter(prefix="/trips/{trip_id}/transports", tags=["transports"])

# при этих статусах отправляем уведомление
NOTIFY_ON_STATUSES = {"delayed", "cancelled", "changed", "landed"}
STATUS_LABELS = {"delayed": "задержан", "cancelled": "отменён", "changed": "изменён", "landed": "приземлился"}

# не уведомляем повторно, если время вылета сдвинулось меньше чем на 10 минут
MEANINGFUL_TIME_CHANGE = timedelta(minutes=10)


def get_owned_transport(db: Session, trip_id: str, transport_id: str) -> Transport:
    """Находит перемещение поездки или отдаёт 404"""

    transport = db.query(Transport).filter(Transport.id == transport_id, Transport.trip_id == trip_id).first()
    if not transport:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Перемещение не найдено")
    return transport


def _set_status(
    db: Session,
    transport: Transport,
    new_status: str,
    user: User,
    trip_id: str,
    actual_departure_datetime=None,
) -> None:
    """Меняет статус перемещения и отправляет уведомление, если рейс задержан, отменён и т.д"""

    previous_status = transport.status
    previous_actual_departure = transport.actual_departure_datetime
    transport.status = new_status
    if actual_departure_datetime is not None:
        transport.actual_departure_datetime = actual_departure_datetime

    status_changed = new_status != previous_status
    time_changed = (
        actual_departure_datetime is not None
        and (
            previous_actual_departure is None
            or abs(actual_departure_datetime - previous_actual_departure) >= MEANINGFUL_TIME_CHANGE
        )
    )
    if (status_changed or time_changed) and new_status in NOTIFY_ON_STATUSES:
        message = f"{transport.departure_location} → {transport.arrival_location}: новый статус: {STATUS_LABELS[new_status]}."
        if actual_departure_datetime:
            message += f" Новое время вылета: {actual_departure_datetime.strftime('%d.%m.%Y %H:%M')}."
        notify(db, user, trip_id, transport.id, "transport_status_changed", "Изменение перемещения", message)


@router.post("/", response_model=TransportOut, status_code=status.HTTP_201_CREATED)
def create_transport(
    trip_id: str,
    data: TransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавление перемещения"""

    get_owned_trip(db, trip_id, current_user.id)
    new_transport = Transport(trip_id=trip_id, **data.model_dump())
    db.add(new_transport)
    db.commit()
    db.refresh(new_transport)
    return new_transport


@router.patch("/{transport_id}", response_model=TransportOut)
def update_transport(
    trip_id: str,
    transport_id: str,
    data: TransportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Изменение перемещения"""

    get_owned_trip(db, trip_id, current_user.id)
    transport = get_owned_transport(db, trip_id, transport_id)

    updates = data.model_dump(exclude_unset=True)
    new_status = updates.pop("status", None)
    # другой рейс или дата: прошлый результат проверки больше не относится к этому перемещению
    if any(field in updates and updates[field] != getattr(transport, field) for field in ("ticket_number", "departure_datetime")):
        transport.flight_summary = None
    reminder_fields = ("departure_location", "arrival_location", "departure_datetime")
    if any(field in updates and updates[field] != getattr(transport, field) for field in reminder_fields):
        forget_reminder(db, "transport_upcoming", transport.id)

    for field, value in updates.items():
        setattr(transport, field, value)

    if new_status:
        _set_status(db, transport, new_status, current_user, trip_id)

    db.commit()
    db.refresh(transport)
    return transport


@router.post("/{transport_id}/refresh-status", response_model=TransportOut)
def refresh_transport_status(
    trip_id: str,
    transport_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновляет статус рейса по данным Aviationstack"""

    get_owned_trip(db, trip_id, current_user.id)
    transport = get_owned_transport(db, trip_id, transport_id)

    try:
        real_status = fetch_real_status(transport)
    except FlightServiceError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(error),
        )
    if real_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Не удалось найти рейс на указанную дату. Проверьте номер рейса и дату вылета",
        )

    _set_status(
        db, transport, real_status["status"], current_user, trip_id,
        actual_departure_datetime=real_status["actual_departure_datetime"],
    )
    transport.actual_departure_datetime = real_status["actual_departure_datetime"]
    transport.flight_summary = real_status["summary"]
    db.commit()
    db.refresh(transport)
    return transport


@router.delete("/{transport_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transport(
    trip_id: str,
    transport_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удаление перемещения"""

    get_owned_trip(db, trip_id, current_user.id)
    found = get_owned_transport(db, trip_id, transport_id)
    db.delete(found)
    db.commit()
