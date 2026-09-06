from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MarketPriceResponse(BaseModel):
    asset_id: UUID
    price: Decimal
    currency: str
    price_timestamp: datetime
    data_source: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")
