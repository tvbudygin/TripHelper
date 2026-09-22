"""Запросы к языковой модели через OpenRouter"""

import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL

REQUEST_TIMEOUT_SECONDS = 30

# отбрасывем мусор модели по типу "User Safety: safe"
MIN_REAL_REPLY_LENGTH = 15
JUNK_REPLY_PREFIXES = ("user safety", "safety:")


def looks_like_real_reply(text: str) -> bool:
    """Проверка, что ответ модели — нормальный текст"""

    stripped = text.strip().lower()
    if len(stripped) < MIN_REAL_REPLY_LENGTH:
        return False
    return not any(stripped.startswith(prefix) for prefix in JUNK_REPLY_PREFIXES)


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
