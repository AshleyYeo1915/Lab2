

OVERSTOCK_LIMIT = 500


total_inventory = 0
failed_entries = 0

print("Inventory Tracker - enter a stock quantity, or type 'quit' to stop.")


while True:
    try:
        user_input = input("Enter stock quantity: ").strip()
    except EOFError:
        break

  
    if user_input.lower() == "quit":
        break

    
    if not user_input.isdigit():
        print(f"Error: '{user_input}' is not a valid whole number. Try again.")
        failed_entries += 1
        continue

 
    quantity = int(user_input)

    
    if quantity < 0:
        print("Error: quantity cannot be negative. Try again.")
        failed_entries += 1
        continue
    else:

        total_inventory += quantity
        print(f"Added {quantity} units. Current total: {total_inventory}")

   
    if total_inventory > OVERSTOCK_LIMIT:
        print(f"ALERT: Overstock! Total inventory ({total_inventory}) exceeds {OVERSTOCK_LIMIT} units.")
        break


print("\n--- Inventory Report ---")
print(f"Total Units Processed: {total_inventory}")
print(f"Number of Failed/Rejected Entries: {failed_entries}")