class Inventory:
    def __init__(self):
        self.__products = []

    def add_product(self, product):
        self.__products.append(product)

    def search_product(self, term):
        term = term.lower()
        for product in self.__products:
            if product.get_product_id().lower() == term or term in product.get_name().lower():
                return product
        return None

    def display_all(self):
        if not self.__products:
            print("\nInventory is empty.")
            return

        print("\nCurrent Inventory:")
        print(f"{'ID':<8}{'Product Name':<20}{'Price ($)':>10}{'Stock':>8}")
        for product in self.__products:
            product.display_information()

    def get_products(self):
        return list(self.__products)

    def next_product_id(self):
        numbers = [int(product.get_product_id()[1:]) for product in self.__products]
        return f"P{max(numbers, default=0) + 1:03d}"
