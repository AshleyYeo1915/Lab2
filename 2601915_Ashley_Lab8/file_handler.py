import json

from inventory import Inventory
from product import Product


def load_inventory(filename):
    inventory = Inventory()

    try:
        with open(filename) as f:
            data = json.load(f)
    except FileNotFoundError:
        return inventory

    for item in data:
        product = Product(item["product_id"], item["name"], item["price"], item["stock"])
        inventory.add_product(product)

    return inventory


def save_inventory(inventory, filename):
    data = []
    for product in inventory.get_products():
        data.append({
            "product_id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
        })

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
