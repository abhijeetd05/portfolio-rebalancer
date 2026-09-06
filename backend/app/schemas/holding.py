from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HoldingBase(BaseModel):
    asset_id: UUID
    units: Decimal = Field(..., gt=0)
    avg_buy_price: Decimal | None = None
    purchase_date: date | None = None

    model_config = ConfigDict(extra="forbid")


class HoldingCreate(HoldingBase):
    """Schema for client-provided holding creation data."""


class HoldingUpdate(BaseModel):
    units: Decimal | None = Field(default=None, gt=0)
    avg_buy_price: Decimal | None = None
    purchase_date: date | None = None

    model_config = ConfigDict(extra="forbid")


class HoldingResponse(BaseModel):
    holding_id: UUID
    portfolio_id: UUID
    asset_id: UUID
    units: Decimal
    avg_buy_price: Decimal | None = None
    purchase_date: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")
