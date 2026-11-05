import json

from digital_product import DigitalProduct
from inventory import Inventory
from physical_product import PhysicalProduct


def load_inventory(filename):
    inventory = Inventory()

    try:
        with open(filename) as f:
            data = json.load(f)
    except FileNotFoundError:
        return inventory

    for item in data:
        product_type = item.get("type")
        common = (item["product_id"], item["name"], item["price"], item["stock"])

        if product_type == "physical":
            product = PhysicalProduct(*common, item["weight"])
        elif product_type == "digital":
            product = DigitalProduct(*common, item["download_size"])
        else:
            print(f"Warning: skipped {item['product_id']} - unknown product type '{product_type}'.")
            continue

        inventory.add_product(product)

    return inventory


def save_inventory(inventory, filename):
    data = []
    for product in inventory.get_products():
        item = {
            "type": None,
            "product_id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
        }

        if isinstance(product, PhysicalProduct):
            item["type"] = "physical"
            item["weight"] = product.get_weight()
        elif isinstance(product, DigitalProduct):
            item["type"] = "digital"
            item["download_size"] = product.get_download_size()

        data.append(item)

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
