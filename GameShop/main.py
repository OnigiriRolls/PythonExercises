from datetime import datetime

from models.user import User
from models.game import Game
from models.order import Order
from models.order_item import OrderItem
from models.order_status import OrderStatus
from services.shop_service import ShopService


def main():
    today = datetime.now()
    users = [
        User(1, "Alex"),
        User(2, "Maria"),
        User(3, "Ana"),
        User(4, "Elena"),
    ]
    print("Created users:")
    for user in users:
        print(f"- {user.user_id}: {user.name}")

    games = [
        Game(1, "Minecraft", 100.0),
        Game(2, "Cyberpunk 2077", 200.0),
        Game(3, "Elden Ring", 250.0),
        Game(4, "Stardew Valley", 60.0),
    ]
    print("\nCreated games:")
    for game in games:
        print(f"- {game.game_id}: {game.name} - {game.price:.2f} lei")

    orders = [
        Order(
            1,
            users[0],
            datetime(2026, 10, 1),
            [OrderItem(games[0], 1, 100.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            2,
            users[0],
            datetime(2026, 10, 5),
            [OrderItem(games[1], 1, 200.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            3,
            users[0],
            datetime(2026, 10, 10),
            [OrderItem(games[2], 1, 250.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            4,
            users[1],
            datetime(2026, 10, 3),
            [OrderItem(games[0], 1, 100.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            5,
            users[1],
            datetime(2026, 10, 8),
            [OrderItem(games[1], 1, 200.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            6,
            users[2],
            datetime(2026, 10, 2),
            [OrderItem(games[0], 1, 100.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            7,
            users[2],
            datetime(2026, 10, 6),
            [OrderItem(games[3], 1, 60.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            8,
            users[2],
            datetime(2026, 10, 11),
            [OrderItem(games[0], 1, 140.0)],
            OrderStatus.COMPLETED,
        ),
        Order(
            9,
            users[3],
            datetime(2026, 10, 4),
            [OrderItem(games[2], 1, 250.0)],
            OrderStatus.CANCELLED,
        ),
        Order(
            10,
            users[0],
            datetime(2026, 9, 1),
            [OrderItem(games[2], 1, 250.0)],
            OrderStatus.COMPLETED,
        ),
    ]

    print("\nCreated orders:")
    for order in orders:
        print(
            f"- Order {order.order_id}: "
            f"{order.user.name}, "
            f"{order.order_date.date()}, "
            f"{order.status.value}, "
            f"{order.get_total():.2f} lei"
        )
    print(f"\nReference date: {today}")

    shop_service = ShopService()
    eligible_users = shop_service.get_eligible_users(users, orders)
    print("\nEligible users:")
    for user in eligible_users:
        print(f"- {user.name}")


if __name__ == "__main__":
    main()
