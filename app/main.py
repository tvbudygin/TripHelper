import os
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError

from app.config import PROJECT_ROOT, UPLOAD_DIR
from app.database import engine, Base, SessionLocal
from app.services.notification_service import generate_notifications_for_all_users
from app.services.trip_service import complete_finished_trips
from app.routers import auth, trips, profile, transport, accommodation, activity, notifications, uploads, chat, expenses

try:
    Base.metadata.create_all(bind=engine)
except OperationalError as error:
    print(f"[TripHelper] База данных недоступна при запуске: {error}")

os.makedirs(UPLOAD_DIR, exist_ok=True)

NOTIFICATION_CHECK_INTERVAL_SECONDS = 300


def run_notification_checker() -> None:
    """Раз в 5 минут создаёт напоминания и завершает поездки, у которых прошла дата окончания"""

    while True:
        db = SessionLocal()
        try:
            generate_notifications_for_all_users(db)
            complete_finished_trips(db)
        except Exception as error:
            print(f"[TripHelper] Ошибка фоновой проверки уведомлений: {error}")
        finally:
            db.close()
        time.sleep(NOTIFICATION_CHECK_INTERVAL_SECONDS)


app = FastAPI(title="TripHelper", description="Сервис-помощник путешественникам")


@app.on_event("startup")
def start_notification_checker() -> None:
    """Запускает фоновую проверку при старте сервера"""

    threading.Thread(target=run_notification_checker, daemon=True).start()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Все роуты API под /api, чтобы не пересекаться со страницами сайта
app.include_router(auth.router, prefix="/api")
app.include_router(trips.router, prefix="/api")
app.include_router(transport.router, prefix="/api")
app.include_router(accommodation.router, prefix="/api")
app.include_router(activity.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")

# Загруженные файлы
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


FRONTEND_DIST = os.path.join(PROJECT_ROOT, "frontend", "dist")

if os.path.isdir(FRONTEND_DIST):
    # Отдаём собранный фронтенд (npm run build) с того же сервера
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        """Отдаёт index.html для любой страницы сайта (дальше работает React Router)"""

        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))
