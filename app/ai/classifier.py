"""Классификатор: определяет тип вопроса пользователя"""

from app.ai.client import ask_model

CATEGORIES = ("trip_info", "recommendation", "off_topic", "stats")

CLASSIFY_PROMPT = """Определи тип вопроса пользователя о путешествии, учитывая историю диалога
(короткий уточняющий ответ вроде "в Ташкенте" — это продолжение предыдущего вопроса, а не новый
не связанный с темой вопрос). Ответь ОДНИМ словом, без пояснений, одним из:
trip_info, recommendation, off_topic, stats.

trip_info — вопрос о его собственной поездке (билеты, жильё, даты, активности).
recommendation — просит совет или рекомендацию (куда пойти, где поесть, что посмотреть).
off_topic — вопрос вообще не связан с путешествиями.
stats — спрашивает про статистику по всем своим поездкам (сколько стран/городов/отелей)."""


# слова, по которым тип вопроса понятен без модели
STATS_WORDS = (
    "статистик", "посещённые страны", "посещенные страны", "посещённые города", "посещенные города",
    "в каких странах", "в каких городах",
)
# отдельные темы статистики: "сколько" + одно из этих слов где угодно в вопросе ("сколько у меня стран").
# "поездок" сюда не входит - сколько у пользователя поездок и куда бот может честно ответить сам,
# по списку поездок в контексте, без отправки в профиль.
STATS_TOPIC_WORDS = ("стран", "город", "отел", "активност", "перемещен")
# при этих словах "сколько" - скорее всего про цену, а не про статистику ("сколько стоит отель")
PRICE_WORDS = ("стоит", "стоил", "цена", "потрат", "бюджет")
RECOMMENDATION_WORDS = (
    "поесть", "поужин", "пообед", "позавтрак", "ресторан", "кафе", "бар ", "посмотреть", "сходить",
    "достопримечательн", "экскурси", "прогуля", "что попробовать", "куда пойти", "чем заняться",
    "посоветуй", "порекомендуй", "рекоменд",
)
TRIP_INFO_WORDS = (
    "вылет", "рейс", "самол", "поезд", "вагон", "билет", "гейт", "платформ", "аэропорт", "вокзал",
    "отел", "жиль", "заселен", "выселен", "бронь", "брони", "адрес", "мой маршрут", "моя поездка",
    "моей поездк", "когда у меня", "во сколько", "бюджет", "потрат", "прилёт", "прилет", "прибыт",
)


def classify_by_keywords(question: str) -> str | None:
    """Определяет тип вопроса по ключевым словам (или None)"""

    text = question.lower()
    if any(word in text for word in STATS_WORDS):
        return "stats"
    if "скольк" in text and not any(word in text for word in PRICE_WORDS) and any(word in text for word in STATS_TOPIC_WORDS):
        return "stats"
    if any(word in text for word in RECOMMENDATION_WORDS):
        return "recommendation"
    if any(word in text for word in TRIP_INFO_WORDS):
        return "trip_info"
    return None


def classify_question(question: str, history: list[dict]) -> str:
    """Возвращает тип вопроса: trip_info, recommendation или off_topic"""

    by_keywords = classify_by_keywords(question)
    if by_keywords:
        return by_keywords

    messages = [{"role": "system", "content": CLASSIFY_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    reply = ask_model(messages)
    if not reply:
        return "trip_info"

    normalized = reply.strip().lower()
    for category in CATEGORIES:
        if category in normalized:
            return category
    return "trip_info"
