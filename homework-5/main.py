from converters import ApiExchangeRateProvider, CurrencyConverter, ExchangeRateProviderError


SUPPORTED_CURRENCIES = ("RUB", "EUR", "GBP", "CNY")


def read_amount() -> float:
    raw_value = input("Введите значение в USD: ").strip()

    try:
        amount = float(raw_value)
    except ValueError as error:
        raise ValueError("Нужно ввести число") from error

    if amount < 0:
        raise ValueError("Сумма не может быть отрицательной")

    return amount


def main() -> None:
    try:
        amount = read_amount()
        provider = ApiExchangeRateProvider()
        converter = CurrencyConverter(provider)

        for currency in SUPPORTED_CURRENCIES:
            converted_amount = converter.convert(amount, currency)
            print(f"{amount} USD to {currency}: {converted_amount:.2f}")

    except (ValueError, ExchangeRateProviderError) as error:
        print(f"Ошибка: {error}")


if __name__ == "__main__":
    main()