from datetime import datetime
from models.court import Court
from models.user import User
from models.booking_status import BookingStatus


class Booking:
    def __init__( self,  booking_id: int,   owner: User,court: Court,  start_time: datetime, end_time: datetime):
        self.booking_id = booking_id
        self.owner = owner
        self.court = court
        self.start_time = start_time
        self.end_time = end_time
        self.status = BookingStatus.ACTIVE
