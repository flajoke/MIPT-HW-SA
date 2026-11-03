import json
import os
import time
from abc import ABC, abstractmethod

import requests


class ExchangeRateProviderError(Exception):
    pass


class ExchangeRateProvider(ABC):
    @abstractmethod
    def get_rates(self) -> dict:
        pass


class ApiExchangeRateProvider(ExchangeRateProvider):
    def __init__(
        self,
        api_url: str = "https://api.exchangerate-api.com/v4/latest/USD",
        cache_file: str = "exchange_rates.json",
        cache_expiry: int = 3600,
        timeout: int = 5,
    ) -> None:
        self.api_url = api_url
        self.cache_file = cache_file
        self.cache_expiry = cache_expiry
        self.timeout = timeout

    def _load_from_cache(self) -> dict | None:
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            timestamp = data["timestamp"]
            rates = data["rates"]

            if time.time() - timestamp < self.cache_expiry:
                return rates
        except (OSError, json.JSONDecodeError, KeyError):
            return None

        return None

    def _save_to_cache(self, rates: dict) -> None:
        data = {
            "timestamp": time.time(),
            "rates": rates,
        }

        with open(self.cache_file, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def get_rates(self) -> dict:
        cached_rates = self._load_from_cache()
        if cached_rates is not None:
            return cached_rates

        try:
            response = requests.get(self.api_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            rates = data["rates"]
            self._save_to_cache(rates)
            return rates
        except (requests.RequestException, json.JSONDecodeError, KeyError) as error:
            raise ExchangeRateProviderError(
                f"Failed to fetch exchange rates: {error}"
            ) from error