from abc import ABC, abstractmethod
from datetime import datetime

from models.user import User
from models.game import Game
from models.order import Order
from models.order_item import OrderItem
from models.order_status import OrderStatus
from services.shop_service import ShopService


class Animal(ABC):
    @abstractmethod
    def eat():
        pass

    def sleep(self):
        print("sleep")


def add_arr(elem, arr=[]):
    arr.append(elem)
    return arr


def main():
    # sett = set()
    # sett.add(1)
    # sett.add(2)
    # for elem in sett:
    #     print(elem)
    # print(3 in sett, 3)
    animal = Animal()
    animal.sleep()

if __name__ == "__main__":
    main()
