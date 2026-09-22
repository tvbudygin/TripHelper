import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    """Хэширует пароль"""

    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""

    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    """Создаёт токен для входа (живёт 24 часа)"""

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


EMAIL_VERIFICATION_EXPIRE_HOURS = 24


def create_email_verification_token(user_id: str) -> str:
    """Создаёт токен для ссылки подтверждения почты"""

    expire = datetime.now(timezone.utc) + timedelta(hours=EMAIL_VERIFICATION_EXPIRE_HOURS)
    payload = {"sub": user_id, "purpose": "email_verification", "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def read_email_verification_token(token: str) -> str | None:
    """Возвращает id пользователя из токена подтверждения почты (или None, если токен не подходит)"""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

    if payload.get("purpose") != "email_verification":
        return None
    return payload.get("sub")
