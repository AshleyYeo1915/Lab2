import gc
import inspect
import weakref
from typing import get_type_hints

from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from inventory import Inventory
from order import Order
from order_line import OrderLine
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier

results: list[bool] = []


def check(description: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {description}")
    results.append(condition)


def heading(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")


def show_product_details(product: Product) -> None:
    # Section 6.2: written only against Product - no subclass checks
    product.display_information()
    print(product.get_fulfilment_info())


def test_association() -> None:
    heading("SECTION 2 - Association: Supplier and Product")
    supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example.com")
    guitar = PhysicalProduct("P001", "Guitar", 350.00, 5, supplier, 4.5)
    software = DigitalProduct("P002", "Photo Editor", 89.90, 100, supplier, 850.0)

    print("Supplier information, reached through each Product:")
    guitar.get_supplier().display_information()
    software.get_supplier().display_information()

    check("Product stores a reference to its Supplier", guitar.get_supplier() is supplier)
    check("Both products refer to the SAME Supplier object (one supplier, many products)",
          guitar.get_supplier() is software.get_supplier())
    check("Supplier and Product are separate objects", guitar is not supplier)

    print("\nPREDICT FIRST: what happens after 'del supplier'?")
    del supplier
    print("After del supplier, through each Product:")
    guitar.get_supplier().display_information()
    software.get_supplier().display_information()
    check("Products still reach the supplier after 'del supplier'",
          guitar.get_supplier().get_name() == "TechSource Pte Ltd")
    print("-> 'del' only removed the variable NAME. The Supplier object stays alive because the")
    print("   products still hold references to it.")

    lonely_supplier = Supplier("S099", "New Vendor", "hello@newvendor.example.com")
    check("A Supplier can exist with no products at all", lonely_supplier.get_name() == "New Vendor")


def test_aggregation() -> None:
    heading("SECTION 3 - Aggregation: Inventory and Product")
    supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example.com")

    keyboard = PhysicalProduct("P003", "Keyboard", 45.90, 20, supplier, 0.9)
    check("Step 1: Product created BEFORE any Inventory exists", keyboard.get_name() == "Keyboard")

    inventory_a = Inventory()
    inventory_b = Inventory()
    inventory_a.add_product(keyboard)
    check("Step 2: Product added to Inventory A", inventory_a.find_product("P003") is keyboard)

    print("\nPREDICT FIRST: will the Product still work after removing it from Inventory A?")
    removed = inventory_a.remove_product("P003")
    check("Step 3: Product no longer in Inventory A", inventory_a.find_product("P003") is None)
    check("remove_product() handed back the very same object", removed is keyboard)
    print("Using the removed product:")
    keyboard.update_stock(25)
    keyboard.display_information()
    check("Removed Product still works (stock updated to 25)", keyboard.get_stock() == 25)

    inventory_b.add_product(keyboard)
    check("Step 4: the SAME Product object added to Inventory B", inventory_b.find_product("P003") is keyboard)

    inventory_b.remove_product("P003")
    check("Emptying an Inventory does not destroy the Product", keyboard.get_price() == 45.90)
    check("find_product() returns None when nothing matches", inventory_b.find_product("P999") is None)


def test_composition() -> None:
    heading("SECTION 4 - Composition: Order and OrderLine")
    supplier = Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example.com")
    laptop = PhysicalProduct("P001", "Laptop", 1200.00, 15, supplier, 2.2)
    mouse = PhysicalProduct("P002", "Mouse", 25.50, 40, supplier, 0.1)
    software = DigitalProduct("P005", "Photo Editor", 89.90, 100, supplier, 850.0)

    order_1 = Order("O001")
    order_1.add_order_line(laptop, 2)
    order_1.add_order_line(mouse, 3)
    order_1.add_order_line(software, 1)
    order_1.display_order()
    check("Order total = 2x1200 + 3x25.50 + 1x89.90 = 2566.40",
          round(order_1.calculate_total(), 2) == 2566.40)
    check("Order created its own OrderLine objects",
          all(isinstance(line, OrderLine) for line in order_1.get_order_lines()))

    print("\nPREDICT FIRST: same Product added to two Orders - how many OrderLines? how many Products?")
    order_2 = Order("O002")
    order_2.add_order_line(laptop, 1)
    line_in_1 = order_1.get_order_lines()[0]
    line_in_2 = order_2.get_order_lines()[0]
    print(f"OrderLine in O001: id={id(line_in_1)}")
    print(f"OrderLine in O002: id={id(line_in_2)}")
    print(f"Product in both:   id={id(line_in_1.get_product())} and id={id(line_in_2.get_product())}")
    check("2 different OrderLine objects (one per Order)", line_in_1 is not line_in_2)
    check("1 shared Product object (OrderLine refers to it, does not own it)",
          line_in_1.get_product() is line_in_2.get_product() is laptop)
    del line_in_1, line_in_2

    check("remove_order_line() removes the Mouse line", order_1.remove_order_line("P002"))
    check("Order now has 2 lines", len(order_1.get_order_lines()) == 2)
    check("Removing a line did not touch the Mouse product", mouse.get_stock() == 40)

    print("\nWhat happens to the OrderLines when the Order itself is removed?")
    line_watchers = [weakref.ref(line) for line in order_1.get_order_lines()]
    del order_1
    gc.collect()
    check("Deleting the Order destroyed its OrderLines (lifecycle tied to the Order)",
          all(watch() is None for watch in line_watchers))
    check("...but the Products they referred to still exist", laptop.get_name() == "Laptop")


def test_type_hints() -> None:
    heading("SECTION 5 - Type hints on every parameter and return value")
    classes = [Supplier, Product, PhysicalProduct, DigitalProduct, CanBeShipped, Inventory, OrderLine, Order]
    missing = []
    for cls in classes:
        for name, member in vars(cls).items():
            if not inspect.isfunction(member) or (name.startswith("__") and name != "__init__"):
                continue
            hints = get_type_hints(member)
            params = [p for p in inspect.signature(member).parameters if p != "self"]
            missing += [f"{cls.__name__}.{name}({p})" for p in params if p not in hints]
            if "return" not in hints:
                missing.append(f"{cls.__name__}.{name} -> return")
    for item in missing:
        print(f"  missing hint: {item}")
    check(f"All methods in {len(classes)} classes have parameter and return type hints", not missing)
    print(f"  e.g. Inventory.find_product: {get_type_hints(Inventory.find_product)}")
    print(f"  e.g. Order.add_order_line:   {get_type_hints(Order.add_order_line)}")


def test_lsp_and_polymorphism() -> None:
    heading("SECTION 6 - Liskov Substitution Principle")
    supplier = Supplier("S003", "CodeWorks Software", "licensing@codeworks.example.com")
    guitar = PhysicalProduct("P007", "Guitar", 350.00, 5, supplier, 4.5)
    os_product = DigitalProduct("P008", "Operating System", 149.00, 50, supplier, 4200.0)

    print("show_product_details(product: Product) with a PhysicalProduct:")
    show_product_details(guitar)
    print("...and with a DigitalProduct, same function, no changes:")
    show_product_details(os_product)
    check("show_product_details() works for both subclasses", True)

    guitar.update_stock(8)
    os_product.update_stock(80)
    check("update_stock() keeps the same meaning in both subclasses",
          guitar.get_stock() == 8 and os_product.get_stock() == 80)
    guitar.update_stock(-1)
    os_product.update_stock(-1)
    check("Both subclasses reject negative stock exactly like Product does",
          guitar.get_stock() == 8 and os_product.get_stock() == 80)

    print("\nDIAGNOSE: the teammate's DigitalProduct.update_stock() that raises NotImplementedError")

    class NoStockDigitalProduct(DigitalProduct):
        def update_stock(self, quantity: int) -> None:
            raise NotImplementedError("Digital products have no stock")

    inventory = Inventory()
    inventory.add_product(guitar)
    inventory.add_product(NoStockDigitalProduct("P009", "Game Pass", 15.00, 999, supplier, 50.0))
    try:
        for product in inventory.get_products():
            product.update_stock(10)
            print(f"  restocked {product.get_name()}")
        crashed = False
    except NotImplementedError as error:
        print(f"  CRASH while restocking: NotImplementedError: {error}")
        crashed = True
    check("The proposed subclass breaks code written for Product (LSP violation demonstrated)", crashed)

    heading("SECTION 7 - Polymorphism through the Product abstraction")
    inventory = Inventory()
    inventory.add_product(guitar)
    inventory.add_product(os_product)
    print("PREDICT FIRST: what will each product print for get_fulfilment_info()?\n")
    outputs = []
    for product in inventory.get_products():   # one loop, no isinstance()
        product.display_information()
        info = product.get_fulfilment_info()
        print(f"  -> {info}")
        outputs.append(info)
    check("PhysicalProduct ran its own get_fulfilment_info()", "shipping" in outputs[0])
    check("DigitalProduct ran its own get_fulfilment_info()", "download" in outputs[1])


def main() -> None:
    test_association()
    test_aggregation()
    test_composition()
    test_type_hints()
    test_lsp_and_polymorphism()
    heading(f"RESULT: {sum(results)}/{len(results)} checks passed")


if __name__ == "__main__":
    main()
