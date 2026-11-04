"""Запросы к языковой модели через OpenRouter"""

import re

import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

REQUEST_TIMEOUT_SECONDS = 30

# отбрасывем мусор модели по типу "User Safety: safe"
MIN_REAL_REPLY_LENGTH = 15
JUNK_REPLY_PREFIXES = ("user safety", "safety:")
# бесплатная модель иногда подмешивает китайский/японский/корейский текст в русский ответ
FOREIGN_SCRIPT_PATTERN = re.compile(r"[一-鿿぀-ヿ가-힯]")


def looks_like_real_reply(text: str) -> bool:
    """Отбрасывает слишком короткий ответ, служебный текст и посторонние иероглифы"""

    stripped = text.strip().lower()
    if len(stripped) < MIN_REAL_REPLY_LENGTH:
        return False
    if stripped.startswith(JUNK_REPLY_PREFIXES):
        return False
    return not FOREIGN_SCRIPT_PATTERN.search(text)


def ask_model(messages: list[dict], model: str = OPENROUTER_MODEL) -> str | None:
    """Отправка сообщения модели и возвращает её ответ (или None, если не получилось)"""

    if not OPENROUTER_API_KEY:
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages}

    try:
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None
