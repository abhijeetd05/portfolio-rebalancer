from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable

from app.engine.deviation import AllocationDeviation


@dataclass(frozen=True)
class TradeRecommendation:
    asset_type: str
    action: str
    trade_value: Decimal
    deviation: Decimal


def calculate_trade_recommendations(
    deviations: Iterable[AllocationDeviation],
    total_portfolio_value: Decimal,
) -> list[TradeRecommendation]:
    """Convert allocation deviations into basic buy and sell recommendations."""
    total_value = Decimal(str(total_portfolio_value))
    recommendations: list[TradeRecommendation] = []

    for deviation in deviations:
        deviation_value = Decimal(str(deviation.deviation))
        if deviation_value == 0:
            continue

        action = "SELL" if deviation_value > 0 else "BUY"
        trade_value = (abs(deviation_value) / Decimal("100")) * total_value
        recommendations.append(
            TradeRecommendation(
                asset_type=deviation.asset_type,
                action=action,
                trade_value=trade_value,
                deviation=deviation_value,
            )
        )

    return sorted(recommendations, key=lambda recommendation: recommendation.asset_type)


def calculate_trades(
    deviations: Iterable[AllocationDeviation],
    total_portfolio_value: Decimal,
) -> list[TradeRecommendation]:
    """Compatibility entry point for basic trade recommendation calculation."""
    return calculate_trade_recommendations(deviations, total_portfolio_value)
