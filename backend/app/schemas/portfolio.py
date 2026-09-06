from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PortfolioBase(BaseModel):
    portfolio_name: str = Field(..., min_length=1, max_length=100)
    base_currency: str = Field(..., min_length=3, max_length=3)

    model_config = ConfigDict(extra="forbid")


class PortfolioCreate(PortfolioBase):
    """Schema for client-provided portfolio creation data."""


class PortfolioUpdate(BaseModel):
    portfolio_name: str | None = Field(default=None, min_length=1, max_length=100)
    base_currency: str | None = Field(default=None, min_length=3, max_length=3)

    model_config = ConfigDict(extra="forbid")


class PortfolioResponse(BaseModel):
    portfolio_id: UUID
    user_id: UUID
    portfolio_name: str
    base_currency: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")
