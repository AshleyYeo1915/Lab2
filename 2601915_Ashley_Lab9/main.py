from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from file_handler import load_inventory, save_inventory
from physical_product import PhysicalProduct

INVENTORY_FILE = "inventory.json"

MENU = """
--- Inventory Menu ---
1. Display all products
2. Add a product
3. Update stock
4. Search for a product
5. Save inventory
6. Exit
"""


def get_input(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return None


def get_whole_number(prompt):
    value = get_input(prompt)
    if value is None or not value.isdigit():
        print(f"Error: '{value}' is not a valid whole number.")
        return None

    return int(value)


def get_decimal(prompt, label):
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


def create_product_from_input(product_id):
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
        weight = get_decimal("Enter Weight (kg): ", "weight")
        if weight is None:
            return None
        return PhysicalProduct(product_id, name, price, stock, weight)

    download_size = get_decimal("Enter Download Size (MB): ", "download size")
    if download_size is None:
        return None
    return DigitalProduct(product_id, name, price, stock, download_size)


def main():
    inventory = load_inventory(INVENTORY_FILE)

    print("Inventory Management System")
    product_count = len(inventory.get_products())
    if product_count:
        print(f"Loaded {product_count} product(s) from {INVENTORY_FILE}.")
    else:
        print(f"No {INVENTORY_FILE} found - starting with an empty inventory.")

    while True:
        print(MENU)
        choice = get_input("Choose an option (1-6): ")

        if choice == "1":
            inventory.display_all()

        elif choice == "2":
            product = create_product_from_input(inventory.next_product_id())
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
            product.display_information()
            print(product.get_fulfilment_info())
            if isinstance(product, CanBeShipped):
                print(f"Shipping cost: ${product.calculate_shipping_cost():.2f}")

        elif choice == "5":
            save_inventory(inventory, INVENTORY_FILE)
            print(f"Inventory successfully saved to {INVENTORY_FILE}")

        elif choice == "6" or choice is None:
            save_inventory(inventory, INVENTORY_FILE)
            print(f"\nInventory successfully saved to {INVENTORY_FILE}. Goodbye!")
            break

        else:
            print(f"Error: '{choice}' is not a valid option. Please choose 1-6.")


if __name__ == "__main__":
    main()
