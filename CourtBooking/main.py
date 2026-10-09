from models.user import User


def main():
    user1 = User(1, "Alex")
    user2 = User(2, "Ana")
    user3 = User(3, "Maria")
    user4 = User(4, "Andrei")
    user5 = User(5, "Sofia")
    print(user1.name)


if __name__ == "__main__":
    main()
