from datetime import datetime

from models.booking import Booking
from models.booking_status import BookingStatus


class BookingService:
    def __init__(self, booking_repository):
        self.booking_repository = booking_repository

    def try_book_court(
        self, booking_id: int, owner, court, start_time: datetime, end_time: datetime
    ) -> bool:

        if not self.is_booking_valid(court, start_time, end_time):
            return False

        self.create_booking(booking_id, owner, court, start_time, end_time)
        return True

    def is_booking_valid(self, court, start_time: datetime, end_time: datetime) -> bool:
        if self.is_time_interval_valid(
            start_time, end_time
        ) and self.is_court_available(court, start_time, end_time):
            return True
        return False

    def is_time_interval_valid(self, start_time: datetime, end_time: datetime) -> bool:
        if end_time <= start_time:
            return False
        return True

    def is_court_available(
        self, court, start_time: datetime, end_time: datetime
    ) -> bool:
        for booking in self.booking_repository.get_all():
            if booking.court.id != court.id:
                continue
            if booking.status == BookingStatus.CANCELLED:
                continue
            overlaps = start_time < booking.end_time and end_time > booking.start_time
            if overlaps:
                return False
        return True

    def create_booking(
        self, booking_id, owner, court, start_time: datetime, end_time: datetime
    ) -> None:
        booking = Booking(booking_id, owner, court, start_time, end_time)
        self.booking_repository.add(booking)
