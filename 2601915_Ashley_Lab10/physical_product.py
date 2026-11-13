from can_be_shipped import CanBeShipped
from product import Product
from supplier import Supplier


class PhysicalProduct(Product, CanBeShipped):
    BASE_SHIPPING_FEE: float = 5.00
    SHIPPING_RATE_PER_KG: float = 2.00

    def __init__(self, product_id: str, name: str, price: float, stock: int,
                 supplier: Supplier, weight: float) -> None:
        super().__init__(product_id, name, price, stock, supplier)
        self.__weight: float = weight

    def get_weight(self) -> float:
        return self.__weight

    def display_information(self) -> None:
        super().display_information()
        print(f"Weight: {self.__weight:.2f} kg")

    def get_fulfilment_info(self) -> str:
        return "Physical product - requires shipping to the customer."

    def calculate_shipping_cost(self) -> float:
        return self.BASE_SHIPPING_FEE + self.__weight * self.SHIPPING_RATE_PER_KG
