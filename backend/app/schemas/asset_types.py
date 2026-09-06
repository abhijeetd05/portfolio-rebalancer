from enum import StrEnum


class AssetType(StrEnum):
    EQUITY = "Equity"
    DEBT = "Debt"
    PRECIOUS_METAL = "Precious Metal"
    CRYPTO = "Crypto"


def normalize_asset_type(value: str) -> AssetType:
    if not isinstance(value, str):
        raise ValueError(
            "asset_type must be one of: Equity, Debt, Precious Metal, Crypto."
        )
    normalized = value.strip().casefold()
    for asset_type in AssetType:
        if asset_type.value.casefold() == normalized:
            return asset_type
    raise ValueError(
        "asset_type must be one of: Equity, Debt, Precious Metal, Crypto."
    )
