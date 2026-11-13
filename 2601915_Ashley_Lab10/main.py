from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from file_handler import load_inventory, save_inventory
from inventory import Inventory
from order import Order
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier

INVENTORY_FILE = "inventory.json"

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


def get_input(prompt: str) -> str | None:
    try:
        return input(prompt).strip()
    except EOFError:
        return None


def get_whole_number(prompt: str) -> int | None:
    value = get_input(prompt)
    if value is None or not value.isdigit():
        print(f"Error: '{value}' is not a valid whole number.")
        return None

    return int(value)


def get_decimal(prompt: str, label: str) -> float | None:
    value = get_input(prompt)
    try:
        number = float(value)
    except (TypeError, ValueError):
        print(f"Error: '{value}' is not a valid {label}.")
        return None

    if number < 0:
        print(f"Error: {label} cannot be negative.")
        return None

    return number


def create_supplier(suppliers: list[Supplier]) -> Supplier | None:
    name = get_input("Enter Supplier Name: ")
    if not name:
        print("Error: supplier name cannot be empty.")
        return None

    email = get_input("Enter Contact Email: ")
    if not email or "@" not in email:
        print(f"Error: '{email}' is not a valid email address.")
        return None

    numbers = [int(supplier.get_supplier_id()[1:]) for supplier in suppliers]
    supplier = Supplier(f"S{max(numbers, default=0) + 1:03d}", name, email)
    suppliers.append(supplier)
    print(f"Created supplier {supplier.get_supplier_id()}.")
    return supplier


def choose_supplier(suppliers: list[Supplier]) -> Supplier | None:
    if suppliers:
        print("\nSuppliers:")
        for supplier in suppliers:
            supplier.display_information()

    supplier_id = get_input("Enter Supplier ID (or N for a new supplier): ")
    if not supplier_id:
        print("Error: please choose a supplier.")
        return None

    if supplier_id.upper() == "N":
        return create_supplier(suppliers)

    for supplier in suppliers:
        if supplier.get_supplier_id().lower() == supplier_id.lower():
            return supplier

    print(f"Error: no supplier with ID '{supplier_id}'.")
    return None


def create_product_from_input(product_id: str, suppliers: list[Supplier]) -> Product | None:
    product_type = get_input("Product type (1 = Physical, 2 = Digital): ")
    if product_type not in ("1", "2"):
        print("Error: please enter 1 for Physical or 2 for Digital.")
        return None

    name = get_input("Enter Product Name: ")
    if not name:
        print("Error: product name cannot be empty.")
        return None

    price = get_decimal("Enter Price: ", "price")
    if price is None:
        return None

    stock = get_whole_number("Enter Stock Quantity: ")
    if stock is None:
        return None

    if product_type == "1":
        extra = get_decimal("Enter Weight (kg): ", "weight")
    else:
        extra = get_decimal("Enter Download Size (MB): ", "download size")
    if extra is None:
        return None

    supplier = choose_supplier(suppliers)
    if supplier is None:
        return None

    if product_type == "1":
        return PhysicalProduct(product_id, name, price, stock, supplier, extra)
    return DigitalProduct(product_id, name, price, stock, supplier, extra)


def show_product_details(product: Product) -> None:
    product.display_information()
    print(product.get_fulfilment_info())
    product.get_supplier().display_information()
    if isinstance(product, CanBeShipped):
        print(f"Shipping cost: ${product.calculate_shipping_cost():.2f}")


def create_order_from_input(inventory: Inventory, order_id: str) -> Order | None:
    order = Order(order_id)
    print(f"\nCreating order {order_id}. Press Enter on an empty line when you are done.")

    while True:
        term = get_input("Product ID or name to order: ")
        if not term:
            break

        product = inventory.search_product(term)
        if product is None:
            print(f"No product found matching '{term}'.")
            continue

        quantity = get_whole_number(f"Quantity of {product.get_name()}: ")
        if quantity is None:
            continue
        if quantity == 0:
            print("Error: quantity must be at least 1.")
            continue

        order.add_order_line(product, quantity)
        print(f"Added {quantity} x {product.get_name()}.")

    if not order.get_order_lines():
        print("Order cancelled - no items were added.")
        return None

    return order


def main() -> None:
    inventory, suppliers = load_inventory(INVENTORY_FILE)
    orders: list[Order] = []

    print("Inventory Management System")
    product_count = len(inventory.get_products())
    if product_count:
        print(f"Loaded {product_count} product(s) and {len(suppliers)} supplier(s) from {INVENTORY_FILE}.")
    else:
        print(f"No {INVENTORY_FILE} found - starting with an empty inventory.")

    while True:
        print(MENU)
        choice = get_input("Choose an option (1-8): ")

        if choice == "1":
            inventory.display_all()

        elif choice == "2":
            product = create_product_from_input(inventory.next_product_id(), suppliers)
            if product is None:
                continue

            inventory.add_product(product)
            print("\nNew Product Added:")
            product.display_information()

        elif choice == "3":
            term = get_input("Enter product ID or name to update: ")
            if not term:
                print("Error: please enter an ID or name.")
                continue

            product = inventory.search_product(term)
            if product is None:
                print(f"No product found matching '{term}'.")
                continue

            stock = get_whole_number(f"Enter new stock for {product.get_name()}: ")
            if stock is None:
                continue

            product.update_stock(stock)
            print(f"Updated {product.get_name()} to {product.get_stock()} units.")

        elif choice == "4":
            term = get_input("Enter product ID or name to search: ")
            if not term:
                print("Error: please enter an ID or name.")
                continue

            product = inventory.search_product(term)
            if product is None:
                print(f"No product found matching '{term}'.")
                continue

            print("\nProduct Found:")
            show_product_details(product)

        elif choice == "5":
            term = get_input("Enter product ID or name to remove: ")
            if not term:
                print("Error: please enter an ID or name.")
                continue

            product = inventory.search_product(term)
            if product is None:
                print(f"No product found matching '{term}'.")
                continue

            inventory.remove_product(product.get_product_id())
            print(f"Removed {product.get_product_id()} {product.get_name()} from the inventory.")

        elif choice == "6":
            order = create_order_from_input(inventory, f"O{len(orders) + 1:03d}")
            if order is not None:
                orders.append(order)
                order.display_order()

        elif choice == "7":
            save_inventory(inventory, suppliers, INVENTORY_FILE)
            print(f"Inventory successfully saved to {INVENTORY_FILE}")

        elif choice == "8" or choice is None:
            save_inventory(inventory, suppliers, INVENTORY_FILE)
            print(f"\nInventory successfully saved to {INVENTORY_FILE}. Goodbye!")
            break

        else:
            print(f"Error: '{choice}' is not a valid option. Please choose 1-8.")


if __name__ == "__main__":
    main()
