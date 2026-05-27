from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Что юзер присылает при регистрации."""

    email: EmailStr
    password: str
    full_name: str


class UserLogin(BaseModel):
    """Что юзер присылает при входе."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Что отдаю фронтенду про юзера (пароль не отдаю)."""

    id: str
    email: str
    full_name: str
    avatar_url: str | None = None

    class Config:
        from_attributes = True
