from can_be_shipped import CanBeShipped
from product import Product


class PhysicalProduct(Product, CanBeShipped):
    BASE_SHIPPING_FEE = 5.00
    SHIPPING_RATE_PER_KG = 2.00

    def __init__(self, product_id, name, price, stock, weight):
        super().__init__(product_id, name, price, stock)
        self.__weight = weight

    def get_weight(self):
        return self.__weight

    def display_information(self):
        super().display_information()
        print(f"  Weight: {self.__weight:.2f} kg")

    def get_fulfilment_info(self):
        return "Physical product - requires shipping to the customer."

    def calculate_shipping_cost(self):
        return self.BASE_SHIPPING_FEE + self.__weight * self.SHIPPING_RATE_PER_KG
