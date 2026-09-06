from __future__ import annotations

from uuid import UUID

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.asset_types import AssetType, normalize_asset_type


class AdminAssetCreate(BaseModel):
    asset_name: str = Field(..., min_length=1, max_length=200)
    asset_type: AssetType
    asset_subtype: str | None = Field(default=None, max_length=50)
    symbol: str | None = Field(default=None, max_length=50)
    external_provider: str = Field(..., min_length=1, max_length=50)
    external_asset_id: str = Field(..., min_length=1, max_length=100)
    currency: str = Field(..., min_length=3, max_length=3)
    data_source: str | None = Field(default=None, max_length=50)

    model_config = ConfigDict(extra="forbid")

    @field_validator("asset_type", mode="before")
    @classmethod
    def canonicalize_asset_type(cls, value: str) -> AssetType:
        return normalize_asset_type(value)

    @field_validator("external_provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized != "yahoo_finance":
            raise ValueError("Only yahoo_finance is currently supported.")
        return normalized

    @field_validator("external_asset_id")
    @classmethod
    def validate_external_id(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not re.fullmatch(r"[A-Z0-9.-]+", normalized):
            raise ValueError("The Yahoo Finance ticker contains unsupported characters.")
        return normalized


class AdminAssetUpdate(BaseModel):
    asset_name: str | None = Field(default=None, min_length=1, max_length=200)
    asset_type: AssetType | None = None
    asset_subtype: str | None = Field(default=None, max_length=50)
    symbol: str | None = Field(default=None, max_length=50)
    external_provider: str | None = Field(default=None, max_length=50)
    external_asset_id: str | None = Field(default=None, max_length=100)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    data_source: str | None = Field(default=None, max_length=50)
    is_active: bool | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("asset_type", mode="before")
    @classmethod
    def canonicalize_asset_type(cls, value: str | None) -> AssetType | None:
        return None if value is None else normalize_asset_type(value)

    @field_validator("external_provider")
    @classmethod
    def validate_provider(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized != "yahoo_finance":
            raise ValueError("Only yahoo_finance is currently supported.")
        return normalized

    @field_validator("external_asset_id")
    @classmethod
    def validate_external_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not re.fullmatch(r"[A-Z0-9.-]+", normalized):
            raise ValueError("The Yahoo Finance ticker contains unsupported characters.")
        return normalized

    @model_validator(mode="after")
    def validate_mapping_pair(self) -> "AdminAssetUpdate":
        if (self.external_provider is None) != (self.external_asset_id is None):
            raise ValueError("external_provider and external_asset_id must be supplied together.")
        return self


class AdminAssetResponse(BaseModel):
    asset_id: UUID
    asset_name: str
    asset_type: str
    asset_subtype: str | None = None
    symbol: str | None = None
    currency: str
    data_source: str | None = None
    external_provider: str | None = None
    external_asset_id: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True, extra="forbid")
