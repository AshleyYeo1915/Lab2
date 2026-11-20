import json

from can_be_shipped import CanBeShipped
from discounts import BulkDiscount, DiscountStrategy, NoDiscount, PercentageDiscount, StudentDiscount
from file_handler import load_inventory, save_inventory
from inventory import Inventory
from order import Order
from product import Product
from product_factory import ProductFactory
from supplier import Supplier
from user_input import get_choice, get_non_negative_int, get_positive_float, get_positive_int, get_text

INVENTORY_FILE = "inventory.json"

# One shared object per strategy - several orders can use the same discount (association, not ownership)
DISCOUNT_OPTIONS: dict[str, DiscountStrategy] = {
    "1": NoDiscount(),
    "2": PercentageDiscount(10),
    "3": BulkDiscount(200, 20),
    "4": StudentDiscount(),
}

MENU = """
--- Inventory Menu ---
1. Display all products
2. Add a product
3. Update stock
4. Search for a product
5. Remove a product
6. Create an order
7. Save inventory
8. Exit
"""


def create_supplier(suppliers: list[Supplier]) -> Supplier:
    name = get_text("Enter Supplier Name: ")
    email = get_text("Enter Contact Email: ")
    while "@" not in email:
        print(f"'{email}' is not a valid email address.")
        email = get_text("Enter Contact Email: ")

    numbers = [int(supplier.get_supplier_id()[1:]) for supplier in suppliers]
    supplier = Supplier(f"S{max(numbers, default=0) + 1:03d}", name, email)
    suppliers.append(supplier)
    print(f"Created supplier {supplier.get_supplier_id()}.")
    return supplier


def choose_supplier(suppliers: list[Supplier]) -> Supplier:
    while True:
        if suppliers:
            print("\nSuppliers:")
            for supplier in suppliers:
                supplier.display_information()

        supplier_id = get_text("Enter Supplier ID (or N for a new supplier): ")
        if supplier_id.upper() == "N":
            return create_supplier(suppliers)

        for supplier in suppliers:
            if supplier.get_supplier_id().lower() == supplier_id.lower():
                return supplier

        print(f"No supplier with ID '{supplier_id}'. Please try again.")


def create_product_from_input(product_id: str, suppliers: list[Supplier]) -> Product:
    choice = get_choice("Product type (1 = Physical, 2 = Digital): ", ("1", "2"))
    product_type = "physical" if choice == "1" else "digital"

    name = get_text("Enter Product Name: ")
    price = get_positive_float("Enter Price: ")
    stock = get_non_negative_int("Enter Stock Quantity: ")
    if product_type == "physical":
        details = {"weight": get_positive_float("Enter Weight (kg): ")}
    else:
        details = {"download_size": get_positive_float("Enter Download Size (MB): ")}
    supplier = choose_supplier(suppliers)

    return ProductFactory.create(product_type, product_id, name, price, stock, supplier, **details)


def show_product_details(product: Product) -> None:
    product.display_information()
    print(product.get_fulfilment_info())
    product.get_supplier().display_information()
    if isinstance(product, CanBeShipped):
        print(f"Shipping cost: ${product.calculate_shipping_cost():.2f}")


def find_product_from_input(inventory: Inventory, action: str) -> Product | None:
    term = get_text(f"Enter product ID or name to {action}: ")
    product = inventory.search_product(term)
    if product is None:
        print(f"No product found matching '{term}'.")
    return product


def create_order_from_input(inventory: Inventory, order_id: str) -> Order | None:
    order = Order(order_id)
    print(f"\nCreating order {order_id}. Press Enter on an empty line when you are done.")

    while True:
        term = input("Product ID or name to order: ").strip()
        if not term:
            break

        product = inventory.search_product(term)
        if product is None:
            print(f"No product found matching '{term}'.")
            continue

        quantity = get_positive_int(f"Quantity of {product.get_name()}: ")
        try:
            order.add_order_line(product, quantity)
        except ValueError as error:
            print(f"Could not add that line: {error}")
            continue
        print(f"Added {quantity} x {product.get_name()}.")

    if not order.get_order_lines():
        print("Order cancelled - no items were added.")
        return None

    print("\nDiscounts:")
    for key, discount in DISCOUNT_OPTIONS.items():
        print(f"{key}. {discount.describe()}")
    choice = get_choice(f"Choose a discount (1-{len(DISCOUNT_OPTIONS)}): ", tuple(DISCOUNT_OPTIONS))
    order.set_discount(DISCOUNT_OPTIONS[choice])
    return order


def save(inventory: Inventory, suppliers: list[Supplier]) -> None:
    try:
        save_inventory(inventory, suppliers, INVENTORY_FILE)
    except OSError as error:
        print(f"Could not save {INVENTORY_FILE}: {error.strerror}. Your changes were NOT saved.")
    else:
        print(f"Inventory successfully saved to {INVENTORY_FILE}")


def run_menu(inventory: Inventory, suppliers: list[Supplier]) -> None:
    orders: list[Order] = []

    while True:
        print(MENU)
        choice = input("Choose an option (1-8): ").strip()

        if choice == "1":
            inventory.display_all()

        elif choice == "2":
            try:
                product = create_product_from_input(inventory.next_product_id(), suppliers)
                inventory.add_product(product)
            except ValueError as error:
                print(f"Could not add product: {error}")
                continue
            print("\nNew Product Added:")
            product.display_information()

        elif choice == "3":
            product = find_product_from_input(inventory, "update")
            if product is None:
                continue

            stock = get_non_negative_int(f"Enter new stock for {product.get_name()}: ")
            try:
                product.update_stock(stock)
            except ValueError as error:
                print(f"Could not update stock: {error}")
                continue
            print(f"Updated {product.get_name()} to {product.get_stock()} units.")

        elif choice == "4":
            product = find_product_from_input(inventory, "search")
            if product is not None:
                print("\nProduct Found:")
                show_product_details(product)

        elif choice == "5":
            product = find_product_from_input(inventory, "remove")
            if product is not None:
                inventory.remove_product(product.get_product_id())
                print(f"Removed {product.get_product_id()} {product.get_name()} from the inventory.")

        elif choice == "6":
            order = create_order_from_input(inventory, f"O{len(orders) + 1:03d}")
            if order is not None:
                orders.append(order)
                order.display_order()

        elif choice == "7":
            save(inventory, suppliers)

        elif choice == "8":
            return

        else:
            print(f"'{choice}' is not a valid option. Please choose 1-8.")


def main() -> None:
    try:
        inventory, suppliers = load_inventory(INVENTORY_FILE)
    except (json.JSONDecodeError, KeyError) as error:
        print(f"Could not read {INVENTORY_FILE} - the file looks damaged ({error}).")
        print("Fix or rename the file, then run the program again. Nothing was changed.")
        return

    print("Inventory Management System")
    product_count = len(inventory.get_products())
    if product_count:
        print(f"Loaded {product_count} product(s) and {len(suppliers)} supplier(s) from {INVENTORY_FILE}.")
    else:
        print(f"No {INVENTORY_FILE} found - starting with an empty inventory.")

    try:
        run_menu(inventory, suppliers)
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended - closing the program.")

    save(inventory, suppliers)
    print("Goodbye!")


if __name__ == "__main__":
    main()
