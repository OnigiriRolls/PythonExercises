from datetime import datetime

from models.user import User
from models.order_item import OrderItem
from models.order_status import OrderStatus


class Order:
    def __init__(
        self,
        order_id: int,
        user: User,
        order_date: datetime,
        items: list[OrderItem],
        status: OrderStatus = OrderStatus.PENDING,
    ):
        self.order_id = order_id
        self.user = user
        self.order_date = order_date
        self.items = items
        self.status = status

    def get_total(self) -> float:
        return sum(item.unit_price * item.quantity for item in self.items)
