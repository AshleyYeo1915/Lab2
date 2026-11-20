from abc import ABC, abstractmethod

from supplier import Supplier


class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, stock: int, supplier: Supplier) -> None:
        # Validation lives in Product because Product owns these rules - every subclass inherits them
        if price <= 0:
            raise ValueError("Price must be greater than zero.")
        if stock < 0:
            raise ValueError("Stock quantity cannot be negative.")

        self.__product_id: str = product_id
        self.__name: str = name
        self.__price: float = price
        self.__stock: int = stock
        # Association: the Supplier is created elsewhere and only referenced here, never owned
        self.__supplier: Supplier = supplier

    def get_product_id(self) -> str:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    def get_supplier(self) -> Supplier:
        return self.__supplier

    def update_stock(self, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative.")

        self.__stock = quantity

    def display_information(self) -> None:
        # end="" leaves the line open so each subclass can add its own details to it
        print(f"{self.__product_id:<6}{self.__name:<24}{self.__price:>10.2f}{self.__stock:>7}  "
              f"{self.__supplier.get_name():<20}", end="")

    @abstractmethod
    def get_fulfilment_info(self) -> str:
        pass
