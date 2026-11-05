import os
import tempfile

from can_be_shipped import CanBeShipped
from digital_product import DigitalProduct
from file_handler import load_inventory, save_inventory
from inventory import Inventory
from physical_product import PhysicalProduct
from product import Product


def check(description, condition):
    print(f"[{'PASS' if condition else 'FAIL'}] {description}")
    return condition


def main():
    results = []

    guitar = PhysicalProduct("P001", "Guitar", 350.00, 5, 4.5)
    feather = PhysicalProduct("P002", "Feather Duster", 8.00, 30, 0.2)
    os_product = DigitalProduct("P003", "Operating System", 149.00, 50, 4200.0)

    print("--- Overridden display_information() ---")
    guitar.display_information()
    os_product.display_information()

    print("\n--- Section 7 checks ---")
    results.append(check("Physical products store their weight", guitar.get_weight() == 4.5))
    results.append(check("Digital products store their download size", os_product.get_download_size() == 4200.0))
    results.append(check("PhysicalProduct implements get_fulfilment_info()", "shipping" in guitar.get_fulfilment_info()))
    results.append(check("DigitalProduct implements get_fulfilment_info()", "download" in os_product.get_fulfilment_info()))

    try:
        Product("P999", "Generic", 1.00, 1)
        blocked = False
    except TypeError as error:
        print(f"       Product(...) raised: {error}")
        blocked = True
    results.append(check("Abstract Product cannot be instantiated directly", blocked))

    results.append(check("Guitar (4.5 kg) shipping = $5 + 4.5 x $2 = $14.00", guitar.calculate_shipping_cost() == 14.00))
    results.append(check("Feather duster (0.2 kg) shipping = $5.40", round(feather.calculate_shipping_cost(), 2) == 5.40))
    results.append(check("PhysicalProduct is a CanBeShipped", isinstance(guitar, CanBeShipped)))
    results.append(check("DigitalProduct is not a CanBeShipped", not isinstance(os_product, CanBeShipped)))

    inventory = Inventory()
    for product in (guitar, feather, os_product):
        inventory.add_product(product)
    results.append(check("Inventory search by name", inventory.search_product("guitar") is guitar))
    results.append(check("Inventory search by ID", inventory.search_product("P003") is os_product))
    results.append(check("Inventory generates the next ID", inventory.next_product_id() == "P004"))
    guitar.update_stock(12)
    results.append(check("Stock updates through update_stock()", guitar.get_stock() == 12))

    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "test_inventory.json")
        save_inventory(inventory, path)
        reloaded = load_inventory(path).get_products()
    types_match = [type(product).__name__ for product in reloaded] == ["PhysicalProduct", "PhysicalProduct", "DigitalProduct"]
    results.append(check("JSON save/load preserves product types", types_match))
    results.append(check("JSON save/load preserves weight and download size",
                         reloaded[0].get_weight() == 4.5 and reloaded[2].get_download_size() == 4200.0))

    print(f"\n{sum(results)}/{len(results)} checks passed")


if __name__ == "__main__":
    main()
