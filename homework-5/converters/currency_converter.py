from abc import ABC, abstractmethod


class BaseCurrencyConverter(ABC):
    @abstractmethod
    def convert(self, amount: float, target_currency: str) -> float:
        pass


class CurrencyConverter(BaseCurrencyConverter):
    def __init__(self, rate_provider) -> None:
        self._rate_provider = rate_provider

    def convert(self, amount: float, target_currency: str) -> float:
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        rates = self._rate_provider.get_rates()

        if target_currency not in rates:
            raise ValueError(f"Unsupported currency: {target_currency}")

        return amount * rates[target_currency]