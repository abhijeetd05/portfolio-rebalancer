from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Protocol


class TargetAllocationLike(Protocol):
    asset_type: str
    target_percentage: Decimal


class AssetClassAllocationLike(Protocol):
    asset_type: str
    allocation_percentage: Decimal


@dataclass(frozen=True)
class AllocationDeviation:
    asset_type: str
    current_percentage: Decimal
    target_percentage: Decimal
    deviation: Decimal


def calculate_deviations(
    current_allocations: Iterable[AssetClassAllocationLike],
    target_allocations: Iterable[TargetAllocationLike],
) -> list[AllocationDeviation]:
    """Compare current and target asset-class allocation percentages."""
    current_by_asset_type = {
        allocation.asset_type: Decimal(str(allocation.allocation_percentage))
        for allocation in current_allocations
    }
    target_by_asset_type = {
        allocation.asset_type: Decimal(str(allocation.target_percentage))
        for allocation in target_allocations
    }

    asset_types = sorted(current_by_asset_type | target_by_asset_type)
    return [
        AllocationDeviation(
            asset_type=asset_type,
            current_percentage=current_by_asset_type.get(asset_type, Decimal("0")),
            target_percentage=target_by_asset_type.get(asset_type, Decimal("0")),
            deviation=(
                current_by_asset_type.get(asset_type, Decimal("0"))
                - target_by_asset_type.get(asset_type, Decimal("0"))
            ),
        )
        for asset_type in asset_types
    ]
