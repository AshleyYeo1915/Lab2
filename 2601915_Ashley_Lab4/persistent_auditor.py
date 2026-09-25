TAX_RATE = 0.10
QUIT = "quit"
INVENTORY_FILE = "inventory.txt"


def load_inventory():
    try:
        with open(INVENTORY_FILE) as f:
            lines = f.read().split()
    except FileNotFoundError:
        return 0, []

    if not lines:
        return 0, []

    return int(lines[0]), [int(amount) for amount in lines[1:]]


def save_inventory(total, history):
    with open(INVENTORY_FILE, "w") as f:
        f.write(f"{total}\n")
        for amount in history:
            f.write(f"{amount}\n")


def get_valid_input():
    try:
        user_input = input("Enter stock quantity: ").strip()
    except EOFError:
        return QUIT

    if user_input.lower() == QUIT:
        return QUIT

    if not user_input.isdigit():
        print(f"Error: '{user_input}' is not a valid whole number. Try again.")
        return None

    return int(user_input)


def process_delivery(current_total, new_value):
    return current_total + new_value


def calculate_tax(amount):
    return amount * TAX_RATE


def generate_report(total_units, failed_attempts, deliveries, history):
    print("\n--- Inventory Report ---")
    print(f"Total Units Processed: {total_units}")
    print(f"Total Deliveries Processed: {deliveries}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")
    print(f"Transaction History: {history}")


total_inventory, history = load_inventory()
deliveries_processed = 0
failed_entries = 0

print("Inventory Tracker - enter a stock quantity, or type 'quit' to stop.")

if history:
    print(f"\nLoaded from {INVENTORY_FILE} - starting total: {total_inventory}")
    print(f"Previous transactions: {history}\n")
else:
    print(f"\nNo saved inventory found - starting a new {INVENTORY_FILE}.\n")

while True:
    entry = get_valid_input()

    if entry == QUIT:
        break

    if entry is None:
        failed_entries += 1
        continue

    total_inventory = process_delivery(total_inventory, entry)
    history.append(entry)
    deliveries_processed += 1
    print(f"Added {entry} units (tax: {calculate_tax(entry):.2f}). Current total: {total_inventory}")

save_inventory(total_inventory, history)
generate_report(total_inventory, failed_entries, deliveries_processed, history)
print(f"\nInventory successfully saved to {INVENTORY_FILE}")
