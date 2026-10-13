import unittest
from datetime import datetime, timedelta

from models.user import User
from models.game import Game
from models.order import Order
from models.order_item import OrderItem
from models.order_status import OrderStatus
from services.shop_service import ShopService


class TestShopService(unittest.TestCase):

    def setUp(self):
        self.reference_date = datetime(2026, 10, 13, 12, 0)
        self.user1 = User(1, "Alex")
        self.user2 = User(2, "Maria")
        self.game = Game(1, "Minecraft", 200.0)
        self.service = ShopService()

    def create_order(
        self, order_id, user, order_date, status=OrderStatus.COMPLETED, price=200.0
    ):
        item = OrderItem(self.game, quantity=1, unit_price=price)
        return Order(order_id, user, order_date, [item], status)

    def test_all_orders_are_older_than_30_days(self):
        orders = [
            self.create_order(1, self.user1, self.reference_date - timedelta(days=31)),
            self.create_order(2, self.user1, self.reference_date - timedelta(days=40)),
            self.create_order(3, self.user1, self.reference_date - timedelta(days=50)),
        ]
        result = self.service.get_eligible_users(
            [self.user1], orders, self.reference_date
        )
        self.assertEqual(result, [])

    def test_all_orders_have_an_ineligible_status(self):
        orders = [
            self.create_order(1, self.user1, self.reference_date, OrderStatus.PENDING),
            self.create_order(
                2, self.user1, self.reference_date, OrderStatus.CANCELLED
            ),
            self.create_order(
                3, self.user1, self.reference_date, OrderStatus.CANCELLED
            ),
        ]

        result = self.service.get_eligible_users(
            [self.user1], orders, self.reference_date
        )
        self.assertEqual(result, [])

    def test_empty_users_list(self):
        orders = [self.create_order(1, self.user1, self.reference_date)]
        result = self.service.get_eligible_users([], orders, self.reference_date)
        self.assertEqual(result, [])

    def test_empty_orders_list(self):
        result = self.service.get_eligible_users(
            [self.user1, self.user2], [], self.reference_date
        )
        self.assertEqual(result, [])

    def test_user_does_not_have_enough_orders(self):
        orders = [
            self.create_order(1, self.user1, self.reference_date, price=250.0),
            self.create_order(
                2, self.user1, self.reference_date - timedelta(days=1), price=250.0
            ),
        ]

        result = self.service.get_eligible_users(
            [self.user1], orders, self.reference_date
        )
        self.assertEqual(result, [])

    def test_total_amount_is_below_500(self):
        orders = [
            self.create_order(1, self.user1, self.reference_date, price=150.0),
            self.create_order(
                2, self.user1, self.reference_date - timedelta(days=1), price=150.0
            ),
            self.create_order(
                3, self.user1, self.reference_date - timedelta(days=2), price=150.0
            ),
        ]

        result = self.service.get_eligible_users(
            [self.user1], orders, self.reference_date
        )
        self.assertEqual(result, [])

    def test_eligible_user_is_returned(self):
        orders = [
            self.create_order(1, self.user1, self.reference_date, price=200.0),
            self.create_order(
                2, self.user1, self.reference_date - timedelta(days=1), price=200.0
            ),
            self.create_order(
                3, self.user1, self.reference_date - timedelta(days=2), price=100.0
            ),
            self.create_order(
                4, self.user2, self.reference_date - timedelta(days=2), price=100.0
            ),
        ]

        result = self.service.get_eligible_users(
            [self.user1, self.user2], orders, self.reference_date
        )
        self.assertEqual(result, [self.user1])

    def test_exact_minimum_orders_and_amount(self):
        orders = [
            self.create_order(1, self.user1, self.reference_date, price=200.0),
            self.create_order(
                2, self.user1, self.reference_date - timedelta(days=1), price=200.0
            ),
            self.create_order(
                3, self.user1, self.reference_date - timedelta(days=2), price=100.0
            ),
        ]

        result = self.service.get_eligible_users(
            [self.user1], orders, self.reference_date
        )
        self.assertEqual(result, [self.user1])

    def test_orders_exactly_30_days_old_are_included(self):
        boundary_date = self.reference_date - timedelta(days=30)
        orders = [
            self.create_order(1, self.user1, boundary_date, price=200.0),
            self.create_order(2, self.user1, boundary_date, price=200.0),
            self.create_order(3, self.user1, boundary_date, price=100.0),
        ]

        result = self.service.get_eligible_users(
            [self.user1], orders, self.reference_date
        )
        self.assertEqual(result, [self.user1])

    def test_order_total_does_not_change_when_game_price_changes(self):
        game = Game(1, "Minecraft", 100.0)
        order_item = OrderItem(game, quantity=1, unit_price=game.price)
        order = Order(
            1, self.user1, self.reference_date, [order_item], OrderStatus.COMPLETED
        )
        orders = [
            order,
            self.create_order(
                2, self.user1, self.reference_date - timedelta(days=1), price=200.0
            ),
            self.create_order(
                3, self.user1, self.reference_date - timedelta(days=2), price=100.0
            ),
        ]

        game.price = 300.0
        result = self.service.get_eligible_users(
            [self.user1], orders, self.reference_date
        )
        self.assertEqual(result, [])
        self.assertEqual(order.get_total(), 100.0)


if __name__ == "__main__":
    unittest.main()
