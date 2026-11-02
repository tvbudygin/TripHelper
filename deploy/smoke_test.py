"""Проверяет регистрацию, вход и поездки на отдельной тестовой базе"""

import json
import sys
import uuid
from urllib.parse import urlencode
from urllib.request import Request, urlopen

base_url = sys.argv[1].rstrip("/")
email = f"check-{uuid.uuid4().hex}@example.com"
password = "TestPassword123!"
token = ""


def request(method, path, data=None, form=False):
    """Отправляет запрос к тестовому приложению"""
    headers = {"Content-Type": "application/x-www-form-urlencoded" if form else "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = (urlencode(data) if form else json.dumps(data)).encode() if data is not None else None
    with urlopen(Request(base_url + path, data=body, headers=headers, method=method), timeout=15) as response:
        content = response.read()
        return json.loads(content) if content else None


request("POST", "/api/auth/register", {"email": email, "password": password, "full_name": "Проверка Docker"})
token = request("POST", "/api/auth/login", {"username": email, "password": password}, form=True)["access_token"]
assert request("GET", "/api/auth/me")["email"] == email
trip = request("POST", "/api/trips/", {
    "title": "Проверка выкладки", "country": "Россия", "city": "Москва",
    "start_date": "2099-05-01", "end_date": "2099-05-05",
})
assert request("GET", f"/api/trips/{trip['id']}")["title"] == "Проверка выкладки"
request("PATCH", f"/api/trips/{trip['id']}", {"title": "Изменено"})
assert request("GET", f"/api/trips/{trip['id']}")["title"] == "Изменено"
request("DELETE", f"/api/trips/{trip['id']}")
print("Регистрация, вход и операции с поездкой работают")
