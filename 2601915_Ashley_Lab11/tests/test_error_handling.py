import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from digital_product import DigitalProduct
from file_handler import load_inventory, load_products, save_inventory
from inventory import Inventory
from physical_product import PhysicalProduct
from product_factory import ProductFactory
from tests.helpers import make_supplier
from user_input import get_positive_float, get_positive_int

PRODUCTS_CSV = Path(__file__).resolve().parent.parent / "products.csv"


def run_quietly(function, *args) -> tuple[object, list[str]]:
    output = io.StringIO()
    with redirect_stdout(output):
        result = function(*args)
    return result, output.getvalue().splitlines()


class TestUserInput(unittest.TestCase):
    def test_positive_float_keeps_asking_until_valid(self) -> None:
        with patch("builtins.input", side_effect=["abc", "-5", "12.50"]):
            value, printed = run_quietly(get_positive_float, "Enter price: ")
        self.assertEqual(value, 12.5)
        self.assertEqual(printed, ["Please enter a valid number, e.g. 12.50",
                                   "Please enter a number greater than zero."])

    def test_positive_int_rejects_text_zero_and_decimals(self) -> None:
        with patch("builtins.input", side_effect=["two", "0", "2.5", "3"]):
            value, printed = run_quietly(get_positive_int, "Quantity: ")
        self.assertEqual(value, 3)
        self.assertEqual(len(printed), 3)


class TestLoadProducts(unittest.TestCase):
    def test_bad_rows_are_skipped_and_valid_rows_load(self) -> None:
        inventory = Inventory()
        _, printed = run_quietly(load_products, str(PRODUCTS_CSV), inventory, make_supplier())
        self.assertEqual([p.get_product_id() for p in inventory.get_products()], ["P001", "D001", "P003"])
        self.assertEqual(printed, [
            "Skipped row 4 (service,S001,Installation,30.00,5): Unknown product type: service",
            "Skipped row 5 (physical,P002,Office Chair,abc,3): could not convert string to float: 'abc'",
            "3 products loaded.",
            "Load attempt finished.",
        ])

    def test_missing_file_is_handled_without_crashing(self) -> None:
        inventory = Inventory()
        _, printed = run_quietly(load_products, "no_such_file.csv", inventory, make_supplier())
        self.assertEqual(printed, ["Products file not found: no_such_file.csv", "Load attempt finished."])
        self.assertEqual(inventory.get_products(), [])


class TestJsonPersistence(unittest.TestCase):
    def test_missing_json_starts_empty(self) -> None:
        inventory, suppliers = load_inventory("no_such_inventory.json")
        self.assertEqual((inventory.get_products(), suppliers), ([], []))

    def test_save_and_load_round_trip_through_the_factory(self) -> None:
        supplier = make_supplier()
        inventory = Inventory()
        inventory.add_product(ProductFactory.create("physical", "P001", "Lamp", 25.00, 10, supplier, weight=1.5))
        inventory.add_product(ProductFactory.create("digital", "D001", "Editor", 49.90, 100, supplier,
                                                    download_size=850))
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "inventory.json")
            save_inventory(inventory, [supplier], path)
            reloaded, suppliers = load_inventory(path)
        lamp, editor = reloaded.get_products()
        self.assertIsInstance(lamp, PhysicalProduct)
        self.assertIsInstance(editor, DigitalProduct)
        self.assertEqual((lamp.get_weight(), editor.get_download_size()), (1.5, 850))
        self.assertEqual(suppliers[0].get_supplier_id(), "S001")


if __name__ == "__main__":
    unittest.main()
