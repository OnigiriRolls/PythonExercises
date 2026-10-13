from models.game import Game


class OrderItem:
    def __init__(self, game: Game, quantity: int, unit_price: float):
        self.game = game
        self.quantity = quantity
        self.unit_price = unit_price
