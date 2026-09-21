TAX_RATE = 0.10
QUIT = "quit"


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


def generate_report(total_units, failed_attempts, deliveries):
    print("\n--- Inventory Report ---")
    print(f"Total Units Processed: {total_units}")
    print(f"Total Deliveries Processed: {deliveries}")
    print(f"Number of Failed/Rejected Entries: {failed_attempts}")


total_inventory = 0
deliveries_processed = 0
failed_entries = 0

print("Inventory Tracker - enter a stock quantity, or type 'quit' to stop.")

while True:
    entry = get_valid_input()

    if entry == QUIT:
        break

    if entry is None:
        failed_entries += 1
        continue

    total_inventory = process_delivery(total_inventory, entry)
    deliveries_processed += 1
    print(f"Added {entry} units (tax: {calculate_tax(entry):.2f}). Current total: {total_inventory}")

generate_report(total_inventory, failed_entries, deliveries_processed)
