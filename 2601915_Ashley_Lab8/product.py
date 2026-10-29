class Product:
    def __init__(self, product_id, name, price, stock):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock

    def get_product_id(self):
        return self.__product_id

    def get_name(self):
        return self.__name

    def get_price(self):
        return self.__price

    def get_stock(self):
        return self.__stock

    def update_stock(self, quantity):
        if quantity < 0:
            print("Error: stock cannot be negative. Stock not changed.")
            return

        self.__stock = quantity

    def display_information(self):
        print(f"{self.__product_id:<8}{self.__name:<20}{self.__price:>10.2f}{self.__stock:>8}")
