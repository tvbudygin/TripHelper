from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserOut
from app.services.auth_service import (
    create_access_token,
    create_email_verification_token,
    hash_password,
    read_email_verification_token,
    verify_password,
)
from app.services.email_service import send_email
from app.config import FRONTEND_BASE_URL, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Находит пользователя по токену"""

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный токен")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Регистрация: создаёт аккаунт и отправляет письмо с подтверждением почты"""

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь с такой почтой уже существует")

    new_user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    background_tasks.add_task(_send_verification_email, new_user)
    return new_user


def _send_verification_email(user: User) -> None:
    """Отправляет письмо со ссылкой для подтверждения почты"""

    token = create_email_verification_token(user.id)
    confirm_link = f"{FRONTEND_BASE_URL}/api/auth/confirm-email?token={token}"
    send_email(
        user.email,
        "Подтвердите почту в TripHelper",
        f"Здравствуйте, {user.full_name}!\n\n"
        f"Подтвердите почту, перейдя по ссылке:\n{confirm_link}\n\n"
        f"Ссылка действует 24 часа.",
    )


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Вход: проверяет почту и пароль, отдаёт токен"""

    found_user = db.query(User).filter(User.email == form_data.username).first()
    if not found_user or not verify_password(form_data.password, found_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная почта или пароль")

    token = create_access_token(data={"sub": found_user.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Данные текущего пользователя"""

    return current_user


@router.get("/confirm-email")
def confirm_email(token: str, db: Session = Depends(get_db)):
    """Подтверждает почту по ссылке из письма"""

    user_id = read_email_verification_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ссылка недействительна или устарела")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    user.is_verified = True
    db.commit()
    return RedirectResponse(url=f"{FRONTEND_BASE_URL}/login?verified=1")
