import re
import unittest
from pathlib import Path

from digital_product import DigitalProduct
from physical_product import PhysicalProduct
from product import Product
from product_factory import ProductFactory
from tests.helpers import make_supplier

PROJECT_FOLDER = Path(__file__).resolve().parent.parent


class TestProductFactory(unittest.TestCase):
    def test_creates_physical_product(self) -> None:
        product = ProductFactory.create("physical", "P001", "Desk Lamp", 25.00, 10, make_supplier(), weight=1.5)
        self.assertIsInstance(product, PhysicalProduct)
        self.assertIsInstance(product, Product)
        self.assertEqual(product.get_weight(), 1.5)

    def test_creates_digital_product(self) -> None:
        product = ProductFactory.create("digital", "D001", "Photo Editor", 49.90, 100, make_supplier(),
                                        download_size=850)
        self.assertIsInstance(product, DigitalProduct)
        self.assertEqual(product.get_download_size(), 850)

    def test_product_type_is_not_case_sensitive(self) -> None:
        product = ProductFactory.create(" Physical ", "P001", "Desk Lamp", 25.00, 10, make_supplier())
        self.assertIsInstance(product, PhysicalProduct)

    def test_unknown_type_raises_clear_value_error(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown product type: service"):
            ProductFactory.create("service", "S001", "Installation", 30.00, 5, make_supplier())

    def test_no_product_is_created_outside_the_factory(self) -> None:
        allowed = {"product_factory.py", "physical_product.py", "digital_product.py"}
        offenders = []
        for path in PROJECT_FOLDER.glob("*.py"):
            if path.name in allowed:
                continue
            for number, line in enumerate(path.read_text().splitlines(), start=1):
                if re.search(r"\b(Physical|Digital)Product\(", line):
                    offenders.append(f"{path.name}:{number}")
        self.assertEqual(offenders, [], "Products should be created through ProductFactory")


if __name__ == "__main__":
    unittest.main()
