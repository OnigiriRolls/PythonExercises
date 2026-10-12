import unittest
from datetime import datetime

from models.user import User
from models.court import Court
from models.booking import Booking
from models.booking_status import BookingStatus
from repositories.booking_repository import BookingRepository
from services.booking_service import BookingService


class TestBookingService(unittest.TestCase):

    def setUp(self):
        self.user1 = User(1, "Alex")
        self.user2 = User(2, "Maria")
        self.court1 = Court(1, "Court 1")
        self.court2 = Court(2, "Court 2")
        self.repository = BookingRepository()
        self.service = BookingService(self.repository)
        self.start_time = datetime(2026, 10, 15, 10, 0)
        self.end_time = datetime(2026, 10, 15, 11, 0)

    def create_booking(
        self, booking_id=1, court=None, start_time=None, end_time=None, owner=None
    ):
        booking = Booking(
            booking_id,
            owner or self.user1,
            court or self.court1,
            start_time or self.start_time,
            end_time or self.end_time,
        )
        self.repository.add(booking)
        return booking

    def test_cancel_changes_booking_status(self):
        booking = Booking(1, self.user1, self.court1, self.start_time, self.end_time)
        booking.cancel()
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_cancel_booking_returns_false_if_booking_does_not_exist(self):
        result = self.service.cancel_booking(999)
        self.assertFalse(result)

    def test_cancel_booking_returns_true_for_existing_booking(self):
        booking = self.create_booking()
        result = self.service.cancel_booking(booking.booking_id)
        self.assertTrue(result)
        self.assertEqual(booking.status, BookingStatus.CANCELLED)

    def test_is_time_interval_valid_returns_false_if_end_is_before_start(self):
        result = self.service.is_time_interval_valid(self.end_time, self.start_time)
        self.assertFalse(result)

    def test_is_time_interval_valid_returns_false_if_times_are_equal(self):
        result = self.service.is_time_interval_valid(self.start_time, self.start_time)
        self.assertFalse(result)

    def test_is_time_interval_valid_returns_true_for_valid_interval(self):
        result = self.service.is_time_interval_valid(self.start_time, self.end_time)
        self.assertTrue(result)

    def test_is_court_available_returns_false_when_bookings_overlap(self):
        self.create_booking()
        new_start = datetime(2026, 10, 15, 10, 30)
        new_end = datetime(2026, 10, 15, 11, 30)
        result = self.service.is_court_available(self.court1, new_start, new_end)
        self.assertFalse(result)

    def test_is_court_available_returns_true_without_overlaps(self):
        self.create_booking()
        new_start = datetime(2026, 10, 15, 11, 0)
        new_end = datetime(2026, 10, 15, 12, 0)
        result = self.service.is_court_available(self.court1, new_start, new_end)
        self.assertTrue(result)

    def test_is_court_available_returns_true_for_cancelled_bookings(self):
        booking = self.create_booking()
        booking.cancel()
        result = self.service.is_court_available(
            self.court1, self.start_time, self.end_time
        )
        self.assertTrue(result)

    def test_is_court_available_returns_true_for_other_courts(self):
        self.create_booking(court=self.court2)
        result = self.service.is_court_available(
            self.court1, self.start_time, self.end_time
        )
        self.assertTrue(result)

    def test_is_booking_valid_returns_false_for_invalid_interval(self):
        result = self.service.is_booking_valid(
            self.court1, self.end_time, self.start_time
        )
        self.assertFalse(result)

    def test_is_booking_valid_returns_false_for_occupied_court(self):
        self.create_booking()
        result = self.service.is_booking_valid(
            self.court1, self.start_time, self.end_time
        )
        self.assertFalse(result)

    def test_try_book_court_returns_true_for_valid_booking(self):
        result = self.service.try_book_court(
            2, self.user2, self.court1, self.start_time, self.end_time
        )
        self.assertTrue(result)

    def test_try_book_court_returns_false_for_occupied_court(self):
        self.create_booking()
        result = self.service.try_book_court(
            2, self.user2, self.court1, self.start_time, self.end_time
        )
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
