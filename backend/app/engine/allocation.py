from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Protocol


class HoldingValuationLike(Protocol):
    asset_type: str
    value: Decimal


class PortfolioValuationLike(Protocol):
    holdings: Iterable[HoldingValuationLike]
    total_value: Decimal


@dataclass(frozen=True)
class AssetClassValuation:
    asset_type: str
    value: Decimal
    allocation_percentage: Decimal


def calculate_current_allocation(
    valuation: PortfolioValuationLike,
) -> list[AssetClassValuation]:
    """Calculate current asset-class allocations from portfolio valuation data."""
    asset_class_values: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for holding in valuation.holdings:
        asset_class_values[holding.asset_type] += Decimal(str(holding.value))

    total_value = sum(asset_class_values.values(), Decimal("0"))
    if total_value == 0:
        return [
            AssetClassValuation(
                asset_type=asset_type,
                value=value,
                allocation_percentage=Decimal("0"),
            )
            for asset_type, value in sorted(asset_class_values.items())
        ]

    return [
        AssetClassValuation(
            asset_type=asset_type,
            value=value,
            allocation_percentage=(value / total_value) * Decimal("100"),
        )
        for asset_type, value in sorted(asset_class_values.items())
    ]


def calculate_allocation(
    valuation: PortfolioValuationLike,
) -> list[AssetClassValuation]:
    """Compatibility entry point for current asset-class allocation calculation."""
    return calculate_current_allocation(valuation)
