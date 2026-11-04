"""Распознавание билетов и броней: достаёт поля формы из PDF или фото"""

import base64
import io
import json
import mimetypes
import re
from datetime import date, datetime

import fitz  # PyMuPDF
from pypdf import PdfReader

from app.ai.client import ask_model, looks_like_real_reply

MAX_ATTEMPTS = 3
MAX_TEXT_LENGTH = 6000
# если текста мало, пробуем распознать первую страницу как картинку
MIN_USABLE_TEXT_LENGTH = 40

PROMPT_RULES = """Верни ТОЛЬКО JSON без пояснений и без markdown-обёртки.
Если поле не удалось определить по документу — поставь null. Не придумывай данные, которых в документе нет.
Даты пиши как "YYYY-MM-DD", время как "HH:MM" (24 часа), дату со временем как "YYYY-MM-DDTHH:MM".
Если в документе не указан год — возьми ближайший будущий. Сегодня {today}.
Города и страны пиши по-русски."""

# поля, которые ищем
FIELDS_BY_KIND = {
    "transport": {
        "type": '"Самолёт" | "Поезд" | "Автобус" | "Автомобиль" | "Паром" | "Другое"',
        "departure_location": "город отправления",
        "arrival_location": "город прибытия",
        "departure_airport": "аэропорт вылета (только для самолёта)",
        "arrival_airport": "аэропорт прилёта (только для самолёта)",
        "departure_datetime": "дата и время отправления (локальное, как в билете)",
        "arrival_datetime": "дата и время прибытия (локальное, как в билете)",
        "price": "стоимость билета числом, без валюты",
        "ticket_number": "номер рейса или поезда, например EK162 или 016А",
        "airline": "авиакомпания или перевозчик",
        "gate_or_platform": "гейт, платформа, путь или перрон",
        "carriage": "номер вагона (для поезда)",
        "seat": "номер места",
    },
    "accommodation": {
        "name": "название отеля/апартаментов",
        "type": '"Отель" | "Апартаменты" | "Хостел" | "Другое"',
        "address": "адрес",
        "check_in_date": "дата заселения",
        "check_out_date": "дата выезда",
        "check_in_time": "время заселения (check-in from)",
        "check_out_time": "время выселения (check-out until)",
        "price": "общая стоимость числом, без валюты",
    },
    "activity": {
        "title": "название места или мероприятия",
        "type": '"Музей" | "Экскурсия" | "Концерт" | "Ресторан" | "Парк" | "Выставка" | "Другое"',
        "visit_date": "дата посещения",
        "visit_time": "время начала/посещения по билету или брони",
        "opening_time": "время открытия места",
        "closing_time": "время закрытия места",
        "address": "адрес",
        "price": "стоимость числом, без валюты",
    },
}

DOCUMENT_TITLES = {
    "transport": "билета на самолёт, поезд, автобус или паром",
    "accommodation": "подтверждения бронирования жилья (отель, апартаменты, хостел)",
    "activity": "билета или брони на экскурсию, музей, концерт, ресторан или другое мероприятие",
}

DATETIME_FIELDS = {"departure_datetime", "arrival_datetime"}
DATE_FIELDS = {"check_in_date", "check_out_date", "visit_date"}
TIME_FIELDS = {"check_in_time", "check_out_time", "visit_time", "opening_time", "closing_time"}
NUMBER_FIELDS = {"price"}


def build_prompt(kind: str) -> str:
    """Сборка инструкции для модели"""

    fields = "\n".join(f'  "{name}": {hint} или null,' for name, hint in FIELDS_BY_KIND[kind].items())
    rules = PROMPT_RULES.format(today=date.today().isoformat())
    return f"Ты извлекаешь данные из {DOCUMENT_TITLES[kind]}.\n{rules}\nФормат ответа:\n{{\n{fields}\n}}"


def _extract_pdf_text(file_bytes: bytes) -> str:
    """Достаёт текст из PDF"""

    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _render_pdf_first_page_as_png(file_bytes: bytes) -> bytes:
    """Превращает первую страницу PDF в картинку"""

    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        page = document.load_page(0)
        pixmap = page.get_pixmap(dpi=150)
        return pixmap.tobytes("png")


def _parse_json_reply(reply: str) -> dict | None:
    """Достаёт JSON из ответа модели"""

    start, end = reply.find("{"), reply.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        parsed = json.loads(reply[start:end + 1])
    except ValueError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _normalize_date(value: str) -> str | None:
    """Привод даты к виду YYYY-MM-DD"""

    text = value.strip()[:10]
    for pattern in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, pattern).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _normalize_time(value: str) -> str | None:
    """Приводит время к виду HH:MM"""

    match = re.search(r"(\d{1,2})[:.](\d{2})", value)
    if not match:
        return None
    hours, minutes = int(match.group(1)), int(match.group(2))
    if hours > 23 or minutes > 59:
        return None
    return f"{hours:02d}:{minutes:02d}"


def _normalize_datetime(value: str) -> str | None:
    """Приводит дату со временем к виду YYYY-MM-DDTHH:MM"""

    text = value.strip()
    try:
        return datetime.fromisoformat(text.replace("Z", "")).strftime("%Y-%m-%dT%H:%M")
    except ValueError:
        pass
    day = _normalize_date(text)
    time = _normalize_time(text[10:] if day else text)
    if day and time:
        return f"{day}T{time}"
    return None


def clean_fields(kind: str, raw: dict) -> dict | None:
    """Оставляет нужные поля и приводит значения к формату формы"""

    result = {}
    for name in FIELDS_BY_KIND[kind]:
        value = raw.get(name)
        if value is None or (isinstance(value, str) and value.strip().lower() in ("", "null", "none", "n/a")):
            continue
        if name in NUMBER_FIELDS:
            match = re.search(r"\d+(?:[.,]\d+)?", str(value).replace(" ", ""))
            value = float(match.group().replace(",", ".")) if match else None
        elif name in DATETIME_FIELDS:
            value = _normalize_datetime(str(value))
        elif name in DATE_FIELDS:
            value = _normalize_date(str(value))
        elif name in TIME_FIELDS:
            value = _normalize_time(str(value))
        else:
            value = str(value).strip()
        if value is not None:
            result[name] = value
    return result or None


def _build_image_messages(prompt: str, image_bytes: bytes, mime_type: str) -> list[dict]:
    """Собирает сообщение для модели из картинки документа"""

    encoded_image = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime_type};base64,{encoded_image}"
    return [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Вот фото документа."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        },
    ]


def parse_document(file_bytes: bytes, filename: str, kind: str) -> dict | None:
    """Распознаёт документ (kind: transport, accommodation или activity). Возвращает поля или None"""

    if kind not in FIELDS_BY_KIND:
        return None

    prompt = build_prompt(kind)
    mime_type, _ = mimetypes.guess_type(filename)

    if mime_type == "application/pdf":
        try:
            text = _extract_pdf_text(file_bytes)
        except Exception:
            text = ""
        if len(text.strip()) >= MIN_USABLE_TEXT_LENGTH:
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text[:MAX_TEXT_LENGTH]},
            ]
        else:
            try:
                page_image = _render_pdf_first_page_as_png(file_bytes)
            except Exception:
                return None
            messages = _build_image_messages(prompt, page_image, "image/png")
    else:
        messages = _build_image_messages(prompt, file_bytes, mime_type or "image/jpeg")

    # модель иногда отвечает мусором или промахивается, поэтому несколько попыток
    for _ in range(MAX_ATTEMPTS):
        reply = ask_model(messages)
        if reply and looks_like_real_reply(reply):
            parsed = _parse_json_reply(reply)
            fields = clean_fields(kind, parsed) if parsed else None
            if fields:
                return fields
    return None
