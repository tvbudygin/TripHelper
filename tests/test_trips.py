"""Проверки создания и изменения поездки без настоящей базы"""
import unittest
from datetime import date
from unittest.mock import Mock, patch
from fastapi import HTTPException
from app.models.trip import Trip
from app.models.user import User
from app.schemas.trip import TripCreate, TripUpdate
from app.routers.trips import create_trip, update_trip


class TripTests(unittest.TestCase):
    """Проверяет даты, владельца и возврат поездки"""

    def setUp(self):
        """Готовит пользователя, поездку и имитирует подключение к базе для теста"""
        self.db = Mock()
        self.user = User(id="user1")
        self.data = TripCreate(title="Отдых", country="Россия", city="Сочи",
            start_date=date(2026, 11, 3), end_date=date(2026, 11, 5))

    def test_creation_assigns_owner(self):
        """Созданная поездка принадлежит вошедшему пользователю"""
        trip = create_trip(self.data, self.db, self.user)
        self.assertEqual(trip.user_id, "user1")
        self.assertEqual(trip.title, "Отдых")
        self.db.add.assert_called_once_with(trip)
        self.db.commit.assert_called_once()

    def test_end_before_start_is_rejected(self):
        """Нельзя сохранить поездку с окончанием раньше начала"""
        self.data.end_date = date(2026, 11, 2)
        with self.assertRaises(HTTPException) as error:
            create_trip(self.data, self.db, self.user)
        self.assertEqual(error.exception.status_code, 400)
        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()

    def test_one_day_trip_is_allowed(self):
        """Начало и конец могут приходиться на один день"""
        self.data.end_date = self.data.start_date
        trip = create_trip(self.data, self.db, self.user)
        self.assertEqual(trip.start_date, trip.end_date)
        self.db.commit.assert_called_once()

    @patch("app.routers.trips.get_owned_trip")
    def test_invalid_date_update_is_rejected(self, get_trip):
        """При изменении одной даты учитывается сохранённая вторая дата"""
        trip = Trip(id="trip1", **self.data.model_dump())
        get_trip.return_value = trip
        with self.assertRaises(HTTPException):
            update_trip("trip1", TripUpdate(start_date=date(2026, 11, 6)), self.db, self.user)
        self.assertEqual(trip.start_date, date(2026, 11, 3))
        self.db.commit.assert_not_called()

    @patch("app.routers.trips.get_owned_trip")
    def test_restoring_blocks_auto_completion(self, get_trip):
        """Возвращённая поездка защищена от повторного автоматического завершения"""
        trip = Trip(id="trip1", is_completed=True, **self.data.model_dump())
        get_trip.return_value = trip
        result = update_trip("trip1", TripUpdate(is_completed=False), self.db, self.user)
        self.assertFalse(result.is_completed)
        self.assertTrue(result.auto_complete_blocked)
        get_trip.assert_called_once_with(self.db, "trip1", "user1")
