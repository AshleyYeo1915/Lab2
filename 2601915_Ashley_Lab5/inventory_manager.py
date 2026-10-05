import json

INVENTORY_FILE = "inventory.json"


def load_inventory():
    try:
        with open(INVENTORY_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_inventory(inventory):
    with open(INVENTORY_FILE, "w") as f:
        json.dump(inventory, f, indent=4)


def display_all(inventory):
    if not inventory:
        print("\nInventory is empty.")
        return

    print("\nCurrent Inventory:")
    print(f"{'ID':<8}{'Product Name':<22}{'Quantity'}")
    for product in inventory:
        print(f"{product['id']:<8}{product['name']:<22}{product['quantity']}")


def add_product(inventory, name, quantity):
    new_id = max([product["id"] for product in inventory], default=1000) + 1
    product = {"id": new_id, "name": name, "quantity": quantity}
    inventory.append(product)
    return product


def search_product(inventory, term):
    for product in inventory:
        if term.isdigit() and product["id"] == int(term):
            return product
        if term.lower() in product["name"].lower():
            return product
    return None


def update_stock(inventory, term, new_quantity):
    product = search_product(inventory, term)
    if product is None:
        return None

    product["quantity"] = new_quantity
    return product


def get_input(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return None


def get_quantity(prompt):
    value = get_input(prompt)
    if value is None or not value.isdigit():
        print(f"Error: '{value}' is not a valid whole number.")
        return None

    return int(value)


MENU = """
--- Inventory Menu ---
1. Display all products
2. Add a product
3. Update stock
4. Search for a product
5. Save inventory
6. Exit
"""

inventory = load_inventory()

print("Inventory Management System")
if inventory:
    print(f"Loaded {len(inventory)} product(s) from {INVENTORY_FILE}.")
else:
    print(f"No {INVENTORY_FILE} found - starting with an empty inventory.")

while True:
    print(MENU)
    choice = get_input("Choose an option (1-6): ")

    if choice == "1":
        display_all(inventory)

    elif choice == "2":
        name = get_input("Enter Product Name: ")
        if not name:
            print("Error: product name cannot be empty.")
            continue

        quantity = get_quantity("Enter Quantity: ")
        if quantity is None:
            continue

        product = add_product(inventory, name, quantity)
        print(f"\nNew Product Added:\n{product['id']},{product['name']},{product['quantity']}")

    elif choice == "3":
        term = get_input("Enter product ID or name to update: ")
        if not term:
            print("Error: please enter an ID or name.")
            continue

        quantity = get_quantity("Enter new quantity: ")
        if quantity is None:
            continue

        product = update_stock(inventory, term, quantity)
        if product is None:
            print(f"No product found matching '{term}'.")
        else:
            print(f"Updated {product['name']} to {product['quantity']} units.")

    elif choice == "4":
        term = get_input("Enter product ID or name to search: ")
        if not term:
            print("Error: please enter an ID or name.")
            continue

        product = search_product(inventory, term)
        if product is None:
            print(f"No product found matching '{term}'.")
        else:
            print(f"Found: {product['id']}, {product['name']}, {product['quantity']}")

    elif choice == "5":
        save_inventory(inventory)
        print(f"Inventory successfully saved to {INVENTORY_FILE}")

    elif choice == "6" or choice is None:
        save_inventory(inventory)
        print(f"\nInventory successfully saved to {INVENTORY_FILE}. Goodbye!")
        break

    else:
        print(f"Error: '{choice}' is not a valid option. Please choose 1-6.")
