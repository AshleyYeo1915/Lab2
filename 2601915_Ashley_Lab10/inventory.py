from product import Product


class Inventory:
    def __init__(self) -> None:
        # Aggregation: typed as the base class so any Product subclass can be stored
        self.__products: list[Product] = []

    def add_product(self, product: Product) -> None:
        self.__products.append(product)

    def remove_product(self, product_id: str) -> Product | None:
        # Only the reference is removed - the Product object itself carries on existing
        product = self.find_product(product_id)
        if product is not None:
            self.__products.remove(product)
        return product

    def find_product(self, product_id: str) -> Product | None:
        for product in self.__products:
            if product.get_product_id().lower() == product_id.lower():
                return product
        return None

    def search_product(self, term: str) -> Product | None:
        product = self.find_product(term)
        if product is not None:
            return product

        for product in self.__products:
            if term.lower() in product.get_name().lower():
                return product
        return None

    def display_all(self) -> None:
        if not self.__products:
            print("\nInventory is empty.")
            return

        print("\nCurrent Inventory:")
        print(f"{'ID':<6}{'Product Name':<24}{'Price ($)':>10}{'Stock':>7}  {'Supplier':<20}Details")
        for product in self.__products:
            product.display_information()

    def get_products(self) -> list[Product]:
        return list(self.__products)

    def next_product_id(self) -> str:
        numbers = [int(product.get_product_id()[1:]) for product in self.__products]
        return f"P{max(numbers, default=0) + 1:03d}"
