from abc import ABC, abstractmethod


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, total: float) -> float:
        pass

    def describe(self) -> str:
        # Not abstract: a plain default that each strategy can override for nicer wording
        return type(self).__name__


class NoDiscount(DiscountStrategy):
    def apply(self, total: float) -> float:
        return total

    def describe(self) -> str:
        return "No discount"


class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float) -> None:
        if not 0 < percentage <= 100:
            raise ValueError("Discount percentage must be between 0 and 100.")
        self.__percentage: float = percentage

    def apply(self, total: float) -> float:
        return total * (1 - self.__percentage / 100)

    def describe(self) -> str:
        return f"{self.__percentage:g}% off"


class BulkDiscount(DiscountStrategy):
    def __init__(self, threshold: float, amount: float) -> None:
        if threshold < 0 or amount <= 0:
            raise ValueError("Bulk discount needs a threshold of 0 or more and an amount greater than zero.")
        self.__threshold: float = threshold
        self.__amount: float = amount

    def apply(self, total: float) -> float:
        if total >= self.__threshold:
            return max(total - self.__amount, 0.0)
        return total

    def describe(self) -> str:
        return f"${self.__amount:.2f} off orders of ${self.__threshold:.2f} or more"


class StudentDiscount(DiscountStrategy):
    # Added in section 2.4 without changing Order: 5% off, but never more than $20 off
    RATE_PERCENT: float = 5.0
    MAX_SAVING: float = 20.00

    def apply(self, total: float) -> float:
        saving = min(total * self.RATE_PERCENT / 100, self.MAX_SAVING)
        return total - saving

    def describe(self) -> str:
        return f"Student discount: {self.RATE_PERCENT:g}% off (max ${self.MAX_SAVING:.2f})"
