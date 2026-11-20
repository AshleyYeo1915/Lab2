def get_text(prompt: str) -> str:
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Please enter a value - it cannot be left blank.")


def get_positive_float(prompt: str) -> float:
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Please enter a number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number, e.g. 12.50")


def get_positive_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Please enter a whole number greater than zero.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number, e.g. 5")


def get_non_negative_int(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))
            if value < 0:
                print("Please enter a whole number of 0 or more.")
                continue
            return value
        except ValueError:
            print("Please enter a valid whole number, e.g. 5")


def get_choice(prompt: str, options: tuple[str, ...]) -> str:
    while True:
        value = input(prompt).strip()
        if value in options:
            return value
        print(f"Please enter one of: {', '.join(options)}")
