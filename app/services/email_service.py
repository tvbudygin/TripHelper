"""Отправка писем через SMTP"""

import smtplib
from email.mime.text import MIMEText

from app.config import SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME

SMTP_TIMEOUT_SECONDS = 10


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Отправляет письмо. Возвращает False, если не получилось"""

    if not SMTP_USERNAME or not SMTP_PASSWORD:
        return False

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = SMTP_USERNAME
    message["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, [to_email], message.as_string())
        return True
    except (smtplib.SMTPException, OSError) as error:
        print(f"[TripHelper] Письмо на {to_email} не отправлено: {error}")
        return False
