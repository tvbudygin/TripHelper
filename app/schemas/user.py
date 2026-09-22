from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Данные для регистрации"""

    email: EmailStr
    password: str
    full_name: str


class UserOut(BaseModel):
    """Данные пользователя для фронтенда"""

    id: str
    email: str
    full_name: str
    avatar_url: str | None = None
    notifications_enabled: bool
    is_verified: bool

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    """Настройки профиля"""

    notifications_enabled: bool
