from models.booking import Booking


class BookingRepository:
    def __init__(self):
        self._bookings: list[Booking] = []

    def add(self, booking: Booking) -> None:
        self._bookings.append(booking)

    def get_all(self) -> list[Booking]:
        return self._bookings.copy()
