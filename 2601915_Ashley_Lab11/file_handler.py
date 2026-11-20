import csv
import json

from digital_product import DigitalProduct
from inventory import Inventory
from physical_product import PhysicalProduct
from product_factory import ProductFactory
from supplier import Supplier


def load_inventory(filename: str) -> tuple[Inventory, list[Supplier]]:
    # FileNotFoundError is handled here (a missing file just means "start empty").
    # A corrupted file (json.JSONDecodeError / KeyError) is left for main() to decide on,
    # because silently starting empty would overwrite the user's data on the next save.
    inventory = Inventory()

    try:
        with open(filename) as f:
            data = json.load(f)
    except FileNotFoundError:
        return inventory, []

    # Suppliers are created on their own first, because they exist independently of any product
    suppliers = [Supplier(item["supplier_id"], item["name"], item["contact_email"])
                 for item in data["suppliers"]]
    suppliers_by_id = {supplier.get_supplier_id(): supplier for supplier in suppliers}

    for item in data["products"]:
        supplier = suppliers_by_id.get(item["supplier_id"])
        if supplier is None:
            print(f"Warning: skipped {item['product_id']} - unknown supplier '{item['supplier_id']}'.")
            continue

        try:
            product = ProductFactory.create(item["type"], item["product_id"], item["name"], item["price"],
                                            item["stock"], supplier, weight=item.get("weight", 0.0),
                                            download_size=item.get("download_size", 0.0))
            inventory.add_product(product)
        except ValueError as error:
            print(f"Warning: skipped {item['product_id']} - {error}")

    return inventory, suppliers


def save_inventory(inventory: Inventory, suppliers: list[Supplier], filename: str) -> None:
    supplier_data = [{
        "supplier_id": supplier.get_supplier_id(),
        "name": supplier.get_name(),
        "contact_email": supplier.get_contact_email(),
    } for supplier in suppliers]

    product_data = []
    for product in inventory.get_products():
        item = {
            "type": None,
            "product_id": product.get_product_id(),
            "name": product.get_name(),
            "price": product.get_price(),
            "stock": product.get_stock(),
            "supplier_id": product.get_supplier().get_supplier_id(),
        }

        if isinstance(product, PhysicalProduct):
            item["type"] = "physical"
            item["weight"] = product.get_weight()
        elif isinstance(product, DigitalProduct):
            item["type"] = "digital"
            item["download_size"] = product.get_download_size()

        product_data.append(item)

    with open(filename, "w") as f:
        json.dump({"suppliers": supplier_data, "products": product_data}, f, indent=4)


def load_products(path: str, inventory: Inventory, supplier: Supplier) -> None:
    try:
        file = open(path, newline="")
    except FileNotFoundError:
        print(f"Products file not found: {path}")
    else:
        loaded = 0
        with file:
            reader = csv.reader(file)
            next(reader, None)  # skip the header row
            for line_number, row in enumerate(reader, start=2):
                try:
                    product_type, product_id, name, price, stock = row
                    product = ProductFactory.create(product_type, product_id, name, float(price),
                                                    int(stock), supplier)
                    inventory.add_product(product)
                    loaded += 1
                except ValueError as error:
                    print(f"Skipped row {line_number} ({','.join(row)}): {error}")
        print(f"{loaded} products loaded.")
    finally:
        print("Load attempt finished.")
