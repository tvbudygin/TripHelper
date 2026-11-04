"""Проверки уведомлений без отправки настоящих писем"""
import unittest
from unittest.mock import Mock, patch
from app.models.user import User
from app.services.notification_service import notify


class NotificationTests(unittest.TestCase):
    """Проверяет условия отправки почтовой копии"""

    def check_notification(self, verified, enabled, delivery=True):
        """Создаёт уведомление с заменой базы и почтового сервиса"""
        db = Mock()
        user = User(id="user1", email="test@example.com",
            is_verified=verified, notifications_enabled=enabled)
        with patch("app.services.notification_service.send_email", return_value=delivery) as send:
            notify(db, user, "trip1", "trip1", "trip_upcoming", "Скоро поездка", "Завтра")
        db.add.assert_called_once()
        notification = db.add.call_args.args[0]
        self.assertEqual(notification.user_id, "user1")
        self.assertEqual(notification.message, "Завтра")
        return send, notification

    def test_verified_email_receives_copy(self):
        """Подтверждённая почта получает копию уведомления"""
        send, notification = self.check_notification(True, True)
        send.assert_called_once_with("test@example.com", "Скоро поездка", "Завтра")
        self.assertTrue(notification.email_sent)

    def test_unverified_email_gets_no_letter(self):
        """Без подтверждения сообщение сохраняется на сайте, письмо не отправляется"""
        send, notification = self.check_notification(False, True)
        send.assert_not_called()
        self.assertFalse(notification.email_sent)

    def test_disabled_email_gets_no_letter(self):
        """Выключенная настройка запрещает отправку почтовой копии"""
        send, notification = self.check_notification(True, False)
        send.assert_not_called()

    def test_delivery_failure_is_saved(self):
        """Неудачная отправка отмечается для последующей повторной попытки"""
        send, notification = self.check_notification(True, True, False)
        send.assert_called_once()
        self.assertFalse(notification.email_sent)
