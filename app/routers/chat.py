from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.ai.chat_service import answer_message
from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.routers.auth import get_current_user
from app.schemas.message import MessageCreate, MessageOut

router = APIRouter(prefix="/chat", tags=["chat"])

# сколько последних сообщений передаём модели как контекст
HISTORY_MESSAGES_LIMIT = 10


@router.get("/messages", response_model=list[MessageOut])
def list_messages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """История чата"""

    return (
        db.query(Message)
        .filter(Message.user_id == current_user.id)
        .order_by(Message.created_at)
        .all()
    )


def _fetch_recent_history(db: Session, user_id: str) -> list[dict]:
    """Последние сообщения диалога для модели"""

    recent = (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(HISTORY_MESSAGES_LIMIT)
        .all()
    )
    recent.reverse()
    return [{"role": message.role, "content": message.content} for message in recent]


@router.post("/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def send_message(
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Сохраняет сообщение пользователя, получает ответ ИИ и сохраняет его"""

    history = _fetch_recent_history(db, current_user.id)

    db.add(Message(user_id=current_user.id, role="user", content=data.content))
    db.commit()

    answer_text = answer_message(db, current_user.id, data.content, history)

    assistant_message = Message(
        user_id=current_user.id,
        role="assistant",
        content=answer_text,
    )
    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)
    return assistant_message
