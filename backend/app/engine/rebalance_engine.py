from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.engine.allocation import (
    AssetClassValuation,
    PortfolioValuationLike,
    calculate_current_allocation,
)
from app.engine.deviation import (
    AllocationDeviation,
    TargetAllocationLike,
    calculate_deviations,
)
from app.engine.trade_calculator import (
    TradeRecommendation,
    calculate_trade_recommendations,
)


@dataclass(frozen=True)
class RebalanceCalculation:
    current_allocations: list[AssetClassValuation]
    deviations: list[AllocationDeviation]
    trade_recommendations: list[TradeRecommendation]


def calculate_rebalance(
    valuation: PortfolioValuationLike,
    target_allocations: Iterable[TargetAllocationLike],
) -> RebalanceCalculation:
    """Orchestrate current allocation, deviation, and trade calculations."""
    current_allocations = calculate_current_allocation(valuation)
    deviations = calculate_deviations(current_allocations, target_allocations)
    trade_recommendations = calculate_trade_recommendations(
        deviations,
        valuation.total_value,
    )

    return RebalanceCalculation(
        current_allocations=current_allocations,
        deviations=deviations,
        trade_recommendations=trade_recommendations,
    )
