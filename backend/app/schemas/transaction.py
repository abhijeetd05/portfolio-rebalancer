from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TransactionCreate(BaseModel):
    asset_id: UUID
    transaction_type: str = Field(..., min_length=1, max_length=20)
    units: Decimal = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    transaction_date: datetime
    fees: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"BUY", "SELL"}:
            raise ValueError("transaction_type must be either 'BUY' or 'SELL'.")
        return normalized


class TransactionUpdate(BaseModel):
    transaction_type: str | None = Field(default=None, min_length=1, max_length=20)
    units: Decimal | None = Field(default=None, gt=0)
    price: Decimal | None = Field(default=None, gt=0)
    transaction_date: datetime | None = None
    fees: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().upper()
        if normalized not in {"BUY", "SELL"}:
            raise ValueError("transaction_type must be either 'BUY' or 'SELL'.")
        return normalized


class TransactionResponse(BaseModel):
    transaction_id: UUID
    portfolio_id: UUID
    asset_id: UUID
    transaction_type: str
    units: Decimal
    price: Decimal
    transaction_date: datetime
    fees: Decimal
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")
