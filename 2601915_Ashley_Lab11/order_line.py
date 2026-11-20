from product import Product


class OrderLine:
    def __init__(self, product: Product, quantity: int) -> None:
        # Validation lives here because the OrderLine owns the rule about its own quantity
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        # Association: the line refers to a Product but does not own it
        self.__product: Product = product
        self.__quantity: int = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def calculate_subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def display_information(self) -> None:
        print(f"{self.__product.get_product_id():<6}{self.__product.get_name():<24}"
              f"{self.__quantity:>5} x {self.__product.get_price():>9.2f} = {self.calculate_subtotal():>10.2f}")
