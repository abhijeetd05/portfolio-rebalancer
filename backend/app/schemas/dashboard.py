from __future__ import annotations

from app.schemas.portfolio import PortfolioResponse
from app.schemas.rebalance import (
    RebalanceActionResponse,
    RebalanceEventResponse,
)
from app.schemas.target_allocation import TargetAllocationResponse
from app.schemas.valuation import PortfolioValuationResponse
from pydantic import BaseModel, ConfigDict


class DashboardRebalanceResponse(BaseModel):
    """Latest persisted rebalance event and its generated actions."""

    event: RebalanceEventResponse
    actions: list[RebalanceActionResponse]

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class DashboardResponse(BaseModel):
    """Read-only composition of the existing portfolio summary data."""

    portfolio: PortfolioResponse
    valuation: PortfolioValuationResponse
    target_allocations: list[TargetAllocationResponse]
    latest_rebalance: DashboardRebalanceResponse | None = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")
