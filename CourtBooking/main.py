from datetime import datetime
from models.user import User
from models.court import Court
from repositories.booking_repository import BookingRepository
from services.booking_service import BookingService


def print_booking_result(user, court, success: bool):
    if success:
        print(f"{user.name} tried booking {court.name}. Successful.")
    else:
        print(f"{user.name} tried booking {court.name}. Court already booked.")


def main():
    user1 = User(1, "Alex")
    user2 = User(2, "Maria")
    user3 = User(3, "Ana")
    court1 = Court(1, "Court 1")
    court2 = Court(2, "Court 2")
    court3 = Court(3, "Court 3")
    print("Created users:", user1.name, user2.name, user3.name)
    print("Created courts:", court1.name, court2.name, court3.name)

    start_time1 = datetime(2026, 10, 15, 10, 0)
    end_time1 = datetime(2026, 10, 15, 11, 0)
    start_time2 = datetime(2026, 10, 15, 11, 0)
    end_time2 = datetime(2026, 10, 15, 12, 0)
    repository = BookingRepository()
    booking_service = BookingService(repository)

    success = booking_service.try_book_court(1, user1, court1, start_time1, end_time1)
    print_booking_result(user1, court1, success)
    success = booking_service.try_book_court(2, user2, court1, start_time1, end_time1)
    print_booking_result(user2, court1, success)
    success = booking_service.try_book_court(3, user3, court3, start_time1, end_time1)
    print_booking_result(user3, court3, success)

    cancelled = booking_service.cancel_booking(1)
    if cancelled:
        print("Booking 1 cancelled successfully.")
    else:
        print("Could not cancel booking 1.")

    success = booking_service.try_book_court(4, user2, court1, start_time1, end_time1)
    print_booking_result(user2, court1, success)


if __name__ == "__main__":
    main()
