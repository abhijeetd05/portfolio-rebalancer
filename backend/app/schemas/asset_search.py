from pydantic import BaseModel, ConfigDict, Field

from app.schemas.asset_types import AssetType


class AssetSearchResult(BaseModel):
    ticker: str
    name: str
    exchange: str | None = None
    asset_type: AssetType | None = None
    currency: str | None = None
    instrument_type: str | None = None
    category: str | None = None
    classification_status: str = "unresolved"

    model_config = ConfigDict(extra="forbid")


class AssetResolveRequest(BaseModel):
    provider: str = Field(default="yahoo_finance", min_length=1, max_length=50)
    ticker: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)
    exchange: str | None = Field(default=None, max_length=50)
    asset_type: AssetType | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    category: str | None = Field(default=None, max_length=200)

    model_config = ConfigDict(extra="forbid")
