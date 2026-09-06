from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RebalanceEventCreate(BaseModel):
    """Client-provided inputs for creating a rebalance event."""

    trigger_type: str = Field(..., min_length=1, max_length=30)
    trigger_date: datetime

    model_config = ConfigDict(extra="forbid")


class RebalanceEventResponse(BaseModel):
    """Persisted rebalance event data returned by the API."""

    rebalance_id: UUID
    portfolio_id: UUID
    trigger_type: str = Field(..., min_length=1, max_length=30)
    trigger_date: datetime
    status: str = Field(..., min_length=1, max_length=30)
    recommended_action: str | None = Field(default=None, max_length=30)
    reason: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class RebalanceActionResponse(BaseModel):
    """Persisted rebalance action data returned with a rebalance event."""

    action_id: UUID
    rebalance_id: UUID
    asset_id: UUID
    action: str = Field(..., min_length=1, max_length=20)
    current_allocation: Decimal = Field(..., max_digits=5, decimal_places=2)
    target_allocation: Decimal = Field(..., max_digits=5, decimal_places=2)
    recommended_value: Decimal = Field(
        ...,
        max_digits=15,
        decimal_places=2,
    )
    reason: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")
