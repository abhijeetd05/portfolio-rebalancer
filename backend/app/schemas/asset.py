from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AssetResponse(BaseModel):
    asset_id: UUID
    asset_name: str
    symbol: str | None = None
    external_provider: str | None = None
    external_asset_id: str | None = None
    asset_type: str
    asset_subtype: str | None = None
    currency: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True, extra="forbid")
