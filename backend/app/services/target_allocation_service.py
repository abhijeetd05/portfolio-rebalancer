from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.target_allocation import TargetAllocation
from app.repositories.target_allocation_repository import TargetAllocationRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.target_allocation import (
    TargetAllocationCreate,
    TargetAllocationUpdate,
)
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)


class TargetAllocationNotFoundError(Exception):
    """Raised when a target allocation does not exist."""

    pass


class TargetAllocationConflictError(Exception):
    """Raised when a target allocation conflicts with an existing allocation."""

    pass


class TargetAllocationTotalExceededError(Exception):
    """Raised when target allocation percentages would exceed 100%."""

    pass


class TargetAllocationService:
    def __init__(
        self,
        target_allocation_repository: TargetAllocationRepository | None = None,
        portfolio_repository: PortfolioRepository | None = None,
    ):
        self.target_allocation_repository = (
            target_allocation_repository or TargetAllocationRepository()
        )
        self.portfolio_repository = (
            portfolio_repository or PortfolioRepository()
        )

    def _get_portfolio_for_user(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ):
        portfolio = self.portfolio_repository.get_by_id(db, portfolio_id)

        if portfolio is None:
            raise PortfolioNotFoundError(
                f"Portfolio {portfolio_id} was not found."
            )

        if portfolio.user_id != user_id:
            raise PortfolioAccessDeniedError(
                f"User {user_id} does not have access to portfolio {portfolio_id}."
            )

        return portfolio

    def create_target_allocation(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        data: TargetAllocationCreate,
    ) -> TargetAllocation:
        self._get_portfolio_for_user(
            db,
            user_id,
            portfolio_id,
        )

        existing = (
            self.target_allocation_repository.get_by_portfolio_and_asset_type(
                db,
                portfolio_id,
                data.asset_type,
            )
        )

        if existing is not None:
            raise TargetAllocationConflictError(
                f"Target allocation already exists for portfolio "
                f"{portfolio_id} and asset type {data.asset_type}."
            )

        allocations = self.target_allocation_repository.get_by_portfolio_id(
            db,
            portfolio_id,
        )
        resulting_total = sum(
            (Decimal(str(item.target_percentage)) for item in allocations),
            Decimal("0"),
        ) + Decimal(str(data.target_percentage))
        if resulting_total > Decimal("100"):
            raise TargetAllocationTotalExceededError(
                f"Target allocation total for portfolio {portfolio_id} "
                f"cannot exceed 100% (resulting total: {resulting_total}%)."
            )

        target_allocation = TargetAllocation(
            portfolio_id=portfolio_id,
            asset_type=data.asset_type,
            target_percentage=data.target_percentage,
        )

        return self.target_allocation_repository.create(
            db,
            target_allocation,
        )

    def get_target_allocation(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        target_id: UUID,
    ) -> TargetAllocation:
        self._get_portfolio_for_user(
            db,
            user_id,
            portfolio_id,
        )

        target_allocation = self.target_allocation_repository.get_by_id(
            db,
            target_id,
        )

        if (
            target_allocation is None
            or target_allocation.portfolio_id != portfolio_id
        ):
            raise TargetAllocationNotFoundError(
                f"Target allocation {target_id} was not found "
                f"in portfolio {portfolio_id}."
            )

        return target_allocation

    def list_target_allocations(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> list[TargetAllocation]:
        self._get_portfolio_for_user(
            db,
            user_id,
            portfolio_id,
        )

        return self.target_allocation_repository.get_by_portfolio_id(
            db,
            portfolio_id,
        )

    def update_target_allocation(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        target_id: UUID,
        data: TargetAllocationUpdate,
    ) -> TargetAllocation:
        target_allocation = self.get_target_allocation(
            db,
            user_id,
            portfolio_id,
            target_id,
        )

        update_data = data.model_dump(exclude_unset=True)
        if "target_percentage" in update_data:
            allocations = self.target_allocation_repository.get_by_portfolio_id(
                db,
                portfolio_id,
            )
            resulting_total = sum(
                (
                    Decimal(str(item.target_percentage))
                    if item.target_id != target_id
                    else Decimal(str(update_data["target_percentage"]))
                    for item in allocations
                ),
                Decimal("0"),
            )
            if resulting_total > Decimal("100"):
                raise TargetAllocationTotalExceededError(
                    f"Target allocation total for portfolio {portfolio_id} "
                    f"cannot exceed 100% (resulting total: {resulting_total}%)."
                )

        updated = self.target_allocation_repository.update(
            db,
            target_id,
            update_data,
        )

        if updated is None:
            raise TargetAllocationNotFoundError(
                f"Target allocation {target_id} was not found "
                f"in portfolio {portfolio_id}."
            )

        return updated

    def delete_target_allocation(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        target_id: UUID,
    ) -> None:
        self.get_target_allocation(
            db,
            user_id,
            portfolio_id,
            target_id,
        )

        deleted = self.target_allocation_repository.delete(
            db,
            target_id,
        )

        if not deleted:
            raise TargetAllocationNotFoundError(
                f"Target allocation {target_id} was not found "
                f"in portfolio {portfolio_id}."
            )