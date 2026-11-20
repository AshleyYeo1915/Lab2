from discounts import DiscountStrategy, NoDiscount
from order_line import OrderLine
from product import Product


class Order:
    def __init__(self, order_id: str, discount: DiscountStrategy | None = None) -> None:
        self.__order_id: str = order_id
        # Composition: only this Order creates these OrderLines, and they live and die with it
        self.__order_lines: list[OrderLine] = []
        # Association (Strategy pattern): the Order uses a discount but does not own it
        self.__discount: DiscountStrategy = discount if discount is not None else NoDiscount()

    def get_order_id(self) -> str:
        return self.__order_id

    def get_discount(self) -> DiscountStrategy:
        return self.__discount

    def set_discount(self, discount: DiscountStrategy) -> None:
        self.__discount = discount

    def add_order_line(self, product: Product, quantity: int) -> None:
        order_line = OrderLine(product, quantity)
        self.__order_lines.append(order_line)

    def remove_order_line(self, product_id: str) -> bool:
        for order_line in self.__order_lines:
            if order_line.get_product().get_product_id().lower() == product_id.lower():
                self.__order_lines.remove(order_line)
                return True
        return False

    def get_order_lines(self) -> tuple[OrderLine, ...]:
        # A tuple is read-only, so outside code can look at the lines but cannot add or move them
        return tuple(self.__order_lines)

    def calculate_subtotal(self) -> float:
        return sum(order_line.calculate_subtotal() for order_line in self.__order_lines)

    def calculate_total(self) -> float:
        # No if/elif about discount types - the strategy object decides
        return self.__discount.apply(self.calculate_subtotal())

    def display_order(self) -> None:
        print(f"\nOrder {self.__order_id}")
        print(f"{'ID':<6}{'Product Name':<24}{'Qty':>5}   {'Price':>9}   {'Subtotal':>10}")
        for order_line in self.__order_lines:
            order_line.display_information()
        subtotal = self.calculate_subtotal()
        total = self.calculate_total()
        print(f"{'Subtotal:':>50}{subtotal:>10.2f}")
        print(f"{'Discount (' + self.__discount.describe() + '):':>50}{total - subtotal:>10.2f}")
        print(f"{'Order total:':>50}{total:>10.2f}")
