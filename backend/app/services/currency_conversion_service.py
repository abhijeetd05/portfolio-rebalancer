from __future__ import annotations

from decimal import Decimal

from app.providers.market_data import MarketDataProvider


class FXRateNotFoundError(ValueError):
    """Raised when a required currency conversion rate is unavailable."""


class CurrencyConversionService:
    def __init__(self, provider: MarketDataProvider) -> None:
        self.provider = provider

    def convert(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:
        source = from_currency.upper()
        target = to_currency.upper()
        if source == target:
            return amount
        rate = self.provider.get_exchange_rate(source, target)
        if rate is None:
            raise FXRateNotFoundError(f"No FX rate found for {source}/{target}.")
        return amount * rate.exchange_rate
