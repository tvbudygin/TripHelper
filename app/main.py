from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, trips, profile

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TripHelper", description="Сервис-помощник путешественникам")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(trips.router)
app.include_router(profile.router)


@app.get("/")
def root():
    """Проверка что сервер вообще работает."""

    return {"message": "TripHelper API работает!"}
