import unittest

from inventory import Inventory
from order import Order
from order_line import OrderLine
from product_factory import ProductFactory
from tests.helpers import make_product, make_supplier


class TestProductValidation(unittest.TestCase):
    def test_price_must_be_greater_than_zero(self) -> None:
        for bad_price in (0, -5):
            with self.subTest(price=bad_price), self.assertRaisesRegex(ValueError, "Price"):
                make_product(price=bad_price)

    def test_stock_cannot_be_negative_for_either_subclass(self) -> None:
        # LSP: the rule set by Product holds for every subclass
        for product_type in ("physical", "digital"):
            with self.subTest(product_type=product_type), self.assertRaisesRegex(ValueError, "Stock"):
                ProductFactory.create(product_type, "X001", "Item", 10.00, -1, make_supplier())

    def test_update_stock_rejects_negative_and_keeps_old_value(self) -> None:
        product = make_product(stock=10)
        with self.assertRaises(ValueError):
            product.update_stock(-1)
        self.assertEqual(product.get_stock(), 10)

    def test_zero_stock_is_allowed(self) -> None:
        self.assertEqual(make_product(stock=0).get_stock(), 0)


class TestOrderValidation(unittest.TestCase):
    def test_order_line_quantity_must_be_greater_than_zero(self) -> None:
        for bad_quantity in (0, -2):
            with self.subTest(quantity=bad_quantity), self.assertRaisesRegex(ValueError, "Quantity"):
                OrderLine(make_product(), bad_quantity)

    def test_invalid_line_is_not_added_to_order(self) -> None:
        order = Order("O001")
        with self.assertRaises(ValueError):
            order.add_order_line(make_product(), 0)
        self.assertEqual(order.get_order_lines(), ())


class TestInventoryValidation(unittest.TestCase):
    def test_duplicate_product_id_is_rejected(self) -> None:
        inventory = Inventory()
        inventory.add_product(make_product("P001"))
        with self.assertRaisesRegex(ValueError, "already in the inventory"):
            inventory.add_product(make_product("P001"))
        self.assertEqual(len(inventory.get_products()), 1)


if __name__ == "__main__":
    unittest.main()
