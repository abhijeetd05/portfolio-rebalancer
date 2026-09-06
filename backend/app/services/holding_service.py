from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.holding import Holding
from app.models.portfolio import Portfolio
from app.repositories.holding_repository import HoldingRepository
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.holding import HoldingCreate, HoldingUpdate
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)


class HoldingNotFoundError(ValueError):
    """Raised when a holding does not exist or does not belong to the requested portfolio."""


class HoldingConflictError(ValueError):
    """Raised when a holding already exists for the same portfolio and asset."""


class HoldingService:
    def __init__(
        self,
        holding_repository: HoldingRepository | None = None,
        portfolio_repository: PortfolioRepository | None = None,
    ) -> None:
        self.holding_repository = holding_repository or HoldingRepository()
        self.portfolio_repository = portfolio_repository or PortfolioRepository()

    def _get_portfolio_for_user(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> Portfolio:
        portfolio = self.portfolio_repository.get_by_id(db, portfolio_id)
        if portfolio is None:
            raise PortfolioNotFoundError(f"Portfolio {portfolio_id} was not found.")
        if portfolio.user_id != user_id:
            raise PortfolioAccessDeniedError(
                f"Portfolio {portfolio_id} does not belong to user {user_id}."
            )
        return portfolio

    def create_holding(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        data: HoldingCreate,
    ) -> Holding:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        existing = self.holding_repository.get_by_portfolio_and_asset(
            db,
            portfolio_id,
            data.asset_id,
        )
        if existing is not None:
            raise HoldingConflictError(
                f"Holding already exists for portfolio {portfolio_id} and asset {data.asset_id}."
            )

        holding = Holding(
            portfolio_id=portfolio_id,
            asset_id=data.asset_id,
            units=data.units,
            avg_buy_price=data.avg_buy_price,
            purchase_date=data.purchase_date,
        )
        return self.holding_repository.create(db, holding)

    def get_holding(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        holding_id: UUID,
    ) -> Holding:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        holding = self.holding_repository.get_by_id(db, holding_id)
        if holding is None or holding.portfolio_id != portfolio_id:
            raise HoldingNotFoundError(
                f"Holding {holding_id} was not found in portfolio {portfolio_id}."
            )
        return holding

    def list_holdings(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> list[Holding]:
        self._get_portfolio_for_user(db, user_id, portfolio_id)
        return self.holding_repository.get_by_portfolio_id(db, portfolio_id)

    def update_holding(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        holding_id: UUID,
        data: HoldingUpdate,
    ) -> Holding:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        holding = self.holding_repository.get_by_id(db, holding_id)
        if holding is None or holding.portfolio_id != portfolio_id:
            raise HoldingNotFoundError(
                f"Holding {holding_id} was not found in portfolio {portfolio_id}."
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return holding

        self.holding_repository.update(db, holding_id, update_data)
        return self.get_holding(db, user_id, portfolio_id, holding_id)

    def delete_holding(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        holding_id: UUID,
    ) -> bool:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        holding = self.holding_repository.get_by_id(db, holding_id)
        if holding is None or holding.portfolio_id != portfolio_id:
            raise HoldingNotFoundError(
                f"Holding {holding_id} was not found in portfolio {portfolio_id}."
            )

        return self.holding_repository.delete(db, holding_id)
