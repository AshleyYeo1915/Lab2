import ast
import inspect
import unittest

from discounts import BulkDiscount, DiscountStrategy, NoDiscount, PercentageDiscount, StudentDiscount
from order import Order
from tests.helpers import make_product


def make_order_totalling_250(discount: DiscountStrategy | None = None) -> Order:
    order = Order("O001", discount)
    order.add_order_line(make_product("P001", price=50.00), 5)   # 5 x 50 = 250
    return order


class TestDiscountStrategies(unittest.TestCase):
    def test_no_discount_returns_total_unchanged(self) -> None:
        self.assertEqual(NoDiscount().apply(250), 250)

    def test_percentage_discount_takes_percentage_off(self) -> None:
        self.assertAlmostEqual(PercentageDiscount(10).apply(250), 225)

    def test_bulk_discount_applies_at_or_above_threshold(self) -> None:
        bulk = BulkDiscount(200, 20)
        self.assertEqual(bulk.apply(250), 230)
        self.assertEqual(bulk.apply(200), 180)

    def test_bulk_discount_ignored_below_threshold(self) -> None:
        self.assertEqual(BulkDiscount(200, 20).apply(150), 150)

    def test_student_discount_is_five_percent_capped_at_twenty(self) -> None:
        self.assertAlmostEqual(StudentDiscount().apply(100), 95)
        self.assertAlmostEqual(StudentDiscount().apply(1000), 980)

    def test_invalid_percentage_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            PercentageDiscount(150)

    def test_discount_strategy_cannot_be_created_directly(self) -> None:
        with self.assertRaises(TypeError):
            DiscountStrategy()


class TestOrderUsesStrategy(unittest.TestCase):
    def test_order_defaults_to_no_discount(self) -> None:
        order = make_order_totalling_250()
        self.assertIsInstance(order.get_discount(), NoDiscount)
        self.assertEqual(order.calculate_total(), 250)

    def test_bulk_then_percentage_with_set_discount(self) -> None:
        order = make_order_totalling_250(BulkDiscount(200, 20))
        self.assertEqual(order.calculate_total(), 230)
        order.set_discount(PercentageDiscount(10))
        self.assertAlmostEqual(order.calculate_total(), 225)

    def test_new_strategy_works_without_changing_order(self) -> None:
        class HalfPriceDiscount(DiscountStrategy):
            def apply(self, total: float) -> float:
                return total / 2

        self.assertEqual(make_order_totalling_250(HalfPriceDiscount()).calculate_total(), 125)

    def test_order_contains_no_discount_if_elif_logic(self) -> None:
        # Parse the real code (comments are ignored) and check calculate_total() has no branching at all
        tree = ast.parse(inspect.getsource(Order.calculate_total).strip())
        branches = [node for node in ast.walk(tree) if isinstance(node, (ast.If, ast.IfExp, ast.Match))]
        self.assertEqual(branches, [], "calculate_total() should leave the discount decision to the strategy")

    def test_two_orders_can_share_one_strategy_object(self) -> None:
        shared = PercentageDiscount(10)
        first, second = make_order_totalling_250(shared), make_order_totalling_250(shared)
        self.assertIs(first.get_discount(), second.get_discount())


if __name__ == "__main__":
    unittest.main()
