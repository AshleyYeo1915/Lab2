from physical_product import PhysicalProduct
from supplier import Supplier


def make_supplier() -> Supplier:
    return Supplier("S001", "TechSource Pte Ltd", "sales@techsource.example.com")


def make_product(product_id: str = "P001", price: float = 50.00, stock: int = 10) -> PhysicalProduct:
    # Built directly (not via the factory) so these helpers do not depend on the code under test
    return PhysicalProduct(product_id, "Test Product", price, stock, make_supplier(), 1.0)
