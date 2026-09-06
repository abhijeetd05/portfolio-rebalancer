from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.repositories.portfolio_repository import PortfolioRepository
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate


class PortfolioNotFoundError(ValueError):
    """Raised when a portfolio does not exist."""


class PortfolioAccessDeniedError(PermissionError):
    """Raised when a portfolio exists but does not belong to the current user."""


class PortfolioService:
    def __init__(self, repository: PortfolioRepository | None = None) -> None:
        self.repository = repository or PortfolioRepository()

    def create_portfolio(
        self,
        db: Session,
        user_id: UUID,
        data: PortfolioCreate,
    ) -> Portfolio:
        portfolio = Portfolio(
            user_id=user_id,
            portfolio_name=data.portfolio_name,
            base_currency=data.base_currency,
        )
        return self.repository.create(db, portfolio)

    def get_portfolio(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> Portfolio:
        portfolio = self.repository.get_by_id(db, portfolio_id)
        if portfolio is None:
            raise PortfolioNotFoundError(f"Portfolio {portfolio_id} was not found.")
        if portfolio.user_id != user_id:
            raise PortfolioAccessDeniedError(
                f"Portfolio {portfolio_id} does not belong to user {user_id}."
            )
        return portfolio

    def list_portfolios(self, db: Session, user_id: UUID) -> list[Portfolio]:
        return self.repository.get_by_user_id(db, user_id)

    def update_portfolio(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        data: PortfolioUpdate,
    ) -> Portfolio:
        portfolio = self.get_portfolio(db, user_id, portfolio_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return portfolio

        self.repository.update(db, portfolio_id, update_data)
        return self.get_portfolio(db, user_id, portfolio_id)

    def delete_portfolio(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> bool:
        self.get_portfolio(db, user_id, portfolio_id)
        return self.repository.delete(db, portfolio_id)
