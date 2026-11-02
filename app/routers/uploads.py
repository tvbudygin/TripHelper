import os
import re
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from app.ai.ticket_parser import parse_document
from app.config import MAX_UPLOAD_SIZE_BYTES, UPLOAD_DIR
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
# имя файла: id владельца, случайный id и расширение
SAVED_FILE_NAME = re.compile(r"[0-9a-f-]{36}_[0-9a-f-]{36}\.(pdf|jpg|jpeg|png)")


async def _validate_and_read(file: UploadFile) -> tuple[str, bytes]:
    """Проверяет тип и размер файла, возвращает расширение и содержимое"""

    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Разрешены только PDF и изображения")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Файл слишком большой (максимум 10 МБ)")

    return extension, content


def _save_file(content: bytes, extension: str, user_id: str) -> str:
    """Сохраняет файл на диск и возвращает ссылку на него"""

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_name = f"{user_id}_{uuid.uuid4()}{extension}"
    with open(os.path.join(UPLOAD_DIR, saved_name), "wb") as saved_file:
        saved_file.write(content)
    return f"/uploads/{saved_name}"


@router.post("/parse", status_code=status.HTTP_201_CREATED)
async def upload_and_parse_document(
    kind: str = "transport",
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Сохраняет файл и распознаёт из него поля формы (kind: transport, accommodation или activity)"""

    extension, content = await _validate_and_read(file)
    document_url = _save_file(content, extension, current_user.id)
    suggested_fields = parse_document(content, file.filename or f"document{extension}", kind)
    return {"url": document_url, "suggested": suggested_fields}


@router.get("/{filename}")
def open_document(filename: str, current_user: User = Depends(get_current_user)):
    """Отдаёт загруженный файл только его владельцу"""

    path = os.path.join(UPLOAD_DIR, filename)
    is_owner = SAVED_FILE_NAME.fullmatch(filename) and filename.startswith(f"{current_user.id}_")
    if not is_owner or not os.path.isfile(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")
    return FileResponse(path)
