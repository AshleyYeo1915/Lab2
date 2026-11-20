import os
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from discounts import BulkDiscount, PercentageDiscount, StudentDiscount
from file_handler import load_products
from inventory import Inventory
from order import Order
from product_factory import ProductFactory
from supplier import Supplier
from user_input import get_positive_float

HERE = Path(__file__).resolve().parent


def heading(title: str) -> None:
    print(f"\n{'=' * 72}\n{title}\n{'=' * 72}")


def count_creation_sites(folder: Path) -> list[str]:
    sites = []
    for path in sorted(folder.glob("*.py")):
        if path.name in ("physical_product.py", "digital_product.py", "predict_first_demo.py")                 or path.name.startswith("test"):
            continue
        for number, line in enumerate(path.read_text().splitlines(), start=1):
            if re.search(r"\b(Physical|Digital)Product\(", line):
                sites.append(f"{path.name}:{number}")
    return sites


def main() -> None:
    supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example.com")
    lamp = ProductFactory.create("physical", "P001", "Desk Lamp", 50.00, 10, supplier, weight=1.5)

    heading("2.1 / 2.4  Adding a 5% student discount")
    order = Order("O001", StudentDiscount())
    order.add_order_line(lamp, 2)
    order.display_order()
    print("\nStudentDiscount is a new class in discounts.py. order.py was not edited to add it.")

    heading("2.3  Order lines adding up to 250")
    order = Order("O002", BulkDiscount(200, 20))
    order.add_order_line(lamp, 5)
    print(f"Subtotal:                                   {order.calculate_subtotal():.2f}")
    print(f"calculate_total() with BulkDiscount(200, 20): {order.calculate_total():.2f}")
    order.set_discount(PercentageDiscount(10))
    print(f"after set_discount(PercentageDiscount(10)):   {order.calculate_total():.2f}")

    heading("2.4  Can two orders share the same PercentageDiscount object?")
    shared = PercentageDiscount(10)
    first, second = Order("O003", shared), Order("O004", shared)
    print(f"first.get_discount() is second.get_discount() -> {first.get_discount() is second.get_discount()}")

    heading("3.2  ProductFactory.create('service', ...) with nothing catching it")
    crash = subprocess.run(
        [sys.executable, "-c",
         "from product_factory import ProductFactory\n"
         "from supplier import Supplier\n"
         "ProductFactory.create('service', 'S001', 'Installation', 30.0, 5, Supplier('S1', 'X', 'x@x.com'))\n"
         "print('this line never runs')"],
        cwd=HERE, capture_output=True, text=True)
    print(f"exit code: {crash.returncode} (non-zero = the program crashed)")
    print("last lines of the traceback:")
    lines = [line for line in crash.stderr.strip().splitlines() if line.strip().strip("~^")]
    for line in lines[-3:]:
        print(f"    {line}")
    print(f"'this line never runs' printed? {'this line never runs' in crash.stdout}")

    heading("3.3  Places that create a PhysicalProduct / DigitalProduct directly")
    lab8 = count_creation_sites(HERE.parent / "2601915_Ashley_Lab10")
    lab9 = count_creation_sites(HERE)
    print(f"Lab 8 (before factory): {len(lab8)} lines in {len({s.split(':')[0] for s in lab8})} files -> {lab8}")
    print(f"Lab 9 (after factory):  {len(lab9)} lines in {len({s.split(':')[0] for s in lab9})} file  -> {lab9}")

    heading("4  Does the stock rule apply to DigitalProduct too?")
    for product_type in ("physical", "digital"):
        try:
            ProductFactory.create(product_type, "X001", "Item", 10.00, -1, supplier)
        except ValueError as error:
            print(f"{product_type:>8} with stock -1 -> ValueError: {error}")

    heading("5.1  get_positive_float() with inputs: abc, -5, 12.50")
    answers = iter(["abc", "-5", "12.50"])

    def fake_input(prompt: str) -> str:
        answer = next(answers)
        print(f"{prompt}{answer}")
        return answer

    with patch("builtins.input", fake_input):
        value = get_positive_float("Enter price: ")
    print(f"returned value: {value!r}")

    heading("5.2  load_products('products.csv', ...)")
    load_products(str(HERE / "products.csv"), Inventory(), supplier)

    heading("5.2  load_products() after products.csv is renamed (file missing)")
    renamed = HERE / "products_renamed.csv"
    os.replace(HERE / "products.csv", renamed)
    try:
        load_products(str(HERE / "products.csv"), Inventory(), supplier)
    finally:
        os.replace(renamed, HERE / "products.csv")
    print("-> except and finally ran; else did not (no 'products loaded' line).")


if __name__ == "__main__":
    main()
