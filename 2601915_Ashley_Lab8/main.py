from file_handler import load_inventory, save_inventory
from product import Product

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


def get_price(prompt):
    value = get_input(prompt)
    try:
        price = float(value)
    except (TypeError, ValueError):
        print(f"Error: '{value}' is not a valid price.")
        return None

    if price < 0:
        print("Error: price cannot be negative.")
        return None

    return price


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
            name = get_input("Enter Product Name: ")
            if not name:
                print("Error: product name cannot be empty.")
                continue

            price = get_price("Enter Price: ")
            if price is None:
                continue

            stock = get_whole_number("Enter Stock Quantity: ")
            if stock is None:
                continue

            product = Product(inventory.next_product_id(), name, price, stock)
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
            else:
                print("\nProduct Found:")
                product.display_information()

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
