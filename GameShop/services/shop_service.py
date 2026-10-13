from datetime import datetime, timedelta

from models.user import User
from models.order import Order
from models.order_status import OrderStatus


class ShopService:

    def get_eligible_users(
        self,
        users: list[User],
        orders: list[Order],
        reference_date: datetime | None = None,
    ) -> list[User]:

        if reference_date is None:
            reference_date = datetime.now()
        cutoff_date = reference_date - timedelta(days=30)
        eligible_users = []

        for user in users:
            completed_orders = [
                order
                for order in orders
                if order.user.user_id == user.user_id
                and order.status == OrderStatus.COMPLETED
                and cutoff_date <= order.order_date <= reference_date
            ]

            total_orders = len(completed_orders)
            total_value = sum(order.get_total() for order in completed_orders)
            if total_orders >= 3 and total_value >= 500:
                eligible_users.append(user)

        return eligible_users
