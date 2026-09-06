from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.models.portfolio import Portfolio
from app.repositories.asset_repository import AssetRepository
from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.services.market_data_service import MarketDataService, MarketPriceNotFoundError
from app.services.currency_conversion_service import CurrencyConversionService
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)


@dataclass(frozen=True)
class HoldingValuation:
    holding_id: UUID
    asset_id: UUID
    asset_name: str
    asset_type: str
    units: Decimal
    price: Decimal
    currency: str
    value: Decimal
    allocation_percentage: Decimal


@dataclass(frozen=True)
class AssetClassValuation:
    asset_type: str
    value: Decimal
    allocation_percentage: Decimal


@dataclass(frozen=True)
class PortfolioValuation:
    portfolio_id: UUID
    portfolio_name: str
    base_currency: str
    total_value: Decimal
    holdings: list[HoldingValuation] = field(default_factory=list)
    asset_class_allocations: list[AssetClassValuation] = field(default_factory=list)


class ValuationService:
    def __init__(
        self,
        holding_repository: HoldingRepository | None = None,
        portfolio_repository: PortfolioRepository | None = None,
        market_data_service: MarketDataService | None = None,
        asset_repository: AssetRepository | None = None,
        currency_conversion_service: CurrencyConversionService | None = None,
    ) -> None:
        self.holding_repository = holding_repository or HoldingRepository()
        self.portfolio_repository = portfolio_repository or PortfolioRepository()
        self.market_data_service = market_data_service
        self.currency_conversion_service = currency_conversion_service
        self.asset_repository = asset_repository or AssetRepository()

    def _get_portfolio_for_user(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> Portfolio:
        portfolio = self.portfolio_repository.get_by_id(db, portfolio_id)
        if portfolio is None:
            raise PortfolioNotFoundError(f"Portfolio {portfolio_id} was not found.")
        if portfolio.user_id != user_id:
            raise PortfolioAccessDeniedError(
                f"Portfolio {portfolio_id} does not belong to user {user_id}."
            )
        return portfolio

    def get_portfolio_valuation(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> PortfolioValuation:
        if self.market_data_service is None:
            raise ValueError("MarketDataService is required for portfolio valuation.")

        portfolio = self._get_portfolio_for_user(db, user_id, portfolio_id)
        holdings = self.holding_repository.get_by_portfolio_id(db, portfolio_id)

        holding_valuations: list[HoldingValuation] = []
        asset_class_values: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))

        for holding in holdings:
            if holding.asset is None:
                asset = self.asset_repository.get_by_id(db, holding.asset_id)
            else:
                asset = holding.asset

            if asset is None:
                raise ValueError(f"Asset {holding.asset_id} was not found for holding {holding.holding_id}.")

            price = self.market_data_service.get_latest_price(asset.asset_id)
            conversion_service = self.currency_conversion_service or CurrencyConversionService(
                self.market_data_service.provider
            )
            holding_value = conversion_service.convert(
                holding.units * price.price,
                price.currency,
                portfolio.base_currency,
            )
            allocation_percentage = Decimal("0")
            holding_valuations.append(
                HoldingValuation(
                    holding_id=holding.holding_id,
                    asset_id=asset.asset_id,
                    asset_name=asset.asset_name,
                    asset_type=asset.asset_type,
                    units=holding.units,
                    price=price.price,
                    currency=price.currency,
                    value=holding_value,
                    allocation_percentage=allocation_percentage,
                )
            )
            asset_class_values[asset.asset_type] += holding_value

        total_value = sum((item.value for item in holding_valuations), Decimal("0"))

        if total_value == 0:
            final_holding_valuations = [
                HoldingValuation(
                    holding_id=item.holding_id,
                    asset_id=item.asset_id,
                    asset_name=item.asset_name,
                    asset_type=item.asset_type,
                    units=item.units,
                    price=item.price,
                    currency=item.currency,
                    value=item.value,
                    allocation_percentage=Decimal("0"),
                )
                for item in holding_valuations
            ]
            final_asset_class_values = [
                AssetClassValuation(
                    asset_type=asset_type,
                    value=value,
                    allocation_percentage=Decimal("0"),
                )
                for asset_type, value in sorted(asset_class_values.items())
            ]
            return PortfolioValuation(
                portfolio_id=portfolio.portfolio_id,
                portfolio_name=portfolio.portfolio_name,
                base_currency=portfolio.base_currency,
                total_value=total_value,
                holdings=final_holding_valuations,
                asset_class_allocations=final_asset_class_values,
            )

        final_holding_valuations: list[HoldingValuation] = []
        for item in holding_valuations:
            allocation_percentage = (item.value / total_value) * Decimal("100")
            final_holding_valuations.append(
                HoldingValuation(
                    holding_id=item.holding_id,
                    asset_id=item.asset_id,
                    asset_name=item.asset_name,
                    asset_type=item.asset_type,
                    units=item.units,
                    price=item.price,
                    currency=item.currency,
                    value=item.value,
                    allocation_percentage=allocation_percentage,
                )
            )

        final_asset_class_values = [
            AssetClassValuation(
                asset_type=asset_type,
                value=value,
                allocation_percentage=(value / total_value) * Decimal("100"),
            )
            for asset_type, value in sorted(asset_class_values.items())
        ]

        return PortfolioValuation(
            portfolio_id=portfolio.portfolio_id,
            portfolio_name=portfolio.portfolio_name,
            base_currency=portfolio.base_currency,
            total_value=total_value,
            holdings=final_holding_valuations,
            asset_class_allocations=final_asset_class_values,
        )
