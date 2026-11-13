import json

from digital_product import DigitalProduct
from inventory import Inventory
from physical_product import PhysicalProduct
from product import Product
from supplier import Supplier


def load_inventory(filename: str) -> tuple[Inventory, list[Supplier]]:
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

        product = create_product(item, supplier)
        if product is None:
            print(f"Warning: skipped {item['product_id']} - unknown product type '{item.get('type')}'.")
            continue

        inventory.add_product(product)

    return inventory, suppliers


def create_product(item: dict, supplier: Supplier) -> Product | None:
    common = (item["product_id"], item["name"], item["price"], item["stock"], supplier)

    if item.get("type") == "physical":
        return PhysicalProduct(*common, item["weight"])
    if item.get("type") == "digital":
        return DigitalProduct(*common, item["download_size"])
    return None


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
