from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HoldingValuationResponse(BaseModel):
    holding_id: UUID
    asset_id: UUID
    asset_name: str
    asset_type: str
    units: Decimal
    price: Decimal
    currency: str
    value: Decimal
    allocation_percentage: Decimal

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class AssetClassAllocationResponse(BaseModel):
    asset_type: str
    value: Decimal
    allocation_percentage: Decimal

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class PortfolioValuationResponse(BaseModel):
    portfolio_id: UUID
    portfolio_name: str
    base_currency: str
    total_value: Decimal
    holdings: list[HoldingValuationResponse]
    asset_class_allocations: list[AssetClassAllocationResponse]

    model_config = ConfigDict(from_attributes=True, extra="forbid")
