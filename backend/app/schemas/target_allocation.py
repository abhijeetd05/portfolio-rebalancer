from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TargetAllocationCreate(BaseModel):
    """Schema for client-provided target allocation creation data."""

    asset_type: str = Field(..., min_length=1, max_length=50)
    target_percentage: Decimal = Field(..., ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class TargetAllocationUpdate(BaseModel):
    """Schema for client-provided target allocation update data."""

    target_percentage: Decimal = Field(..., ge=0, le=100)

    model_config = ConfigDict(extra="forbid")


class TargetAllocationResponse(BaseModel):
    """Schema for target allocation response data."""

    target_allocation_id: UUID = Field(..., alias="target_id")
    portfolio_id: UUID
    asset_type: str
    target_percentage: Decimal
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")
