from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)


class TransactionNotFoundError(ValueError):
    """Raised when a transaction does not exist or does not belong to the requested portfolio."""


class TransactionService:
    def __init__(
        self,
        transaction_repository: TransactionRepository | None = None,
        portfolio_repository: PortfolioRepository | None = None,
    ) -> None:
        self.transaction_repository = transaction_repository or TransactionRepository()
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

    def create_transaction(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        data: TransactionCreate,
    ) -> Transaction:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        transaction = Transaction(
            portfolio_id=portfolio_id,
            asset_id=data.asset_id,
            transaction_type=data.transaction_type,
            units=data.units,
            price=data.price,
            transaction_date=data.transaction_date,
            fees=data.fees,
            notes=data.notes,
        )
        return self.transaction_repository.create(db, transaction)

    def get_transaction(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        transaction_id: UUID,
    ) -> Transaction:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        transaction = self.transaction_repository.get_by_id(db, transaction_id)
        if transaction is None or transaction.portfolio_id != portfolio_id:
            raise TransactionNotFoundError(
                f"Transaction {transaction_id} was not found in portfolio {portfolio_id}."
            )
        return transaction

    def list_transactions(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> list[Transaction]:
        self._get_portfolio_for_user(db, user_id, portfolio_id)
        return self.transaction_repository.get_by_portfolio_id(db, portfolio_id)

    def list_transactions_by_asset(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        asset_id: UUID,
    ) -> list[Transaction]:
        self._get_portfolio_for_user(db, user_id, portfolio_id)
        return self.transaction_repository.get_by_portfolio_and_asset(
            db,
            portfolio_id,
            asset_id,
        )

    def update_transaction(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        transaction_id: UUID,
        data: TransactionUpdate,
    ) -> Transaction:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        transaction = self.transaction_repository.get_by_id(db, transaction_id)
        if transaction is None or transaction.portfolio_id != portfolio_id:
            raise TransactionNotFoundError(
                f"Transaction {transaction_id} was not found in portfolio {portfolio_id}."
            )

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return transaction

        self.transaction_repository.update(db, transaction_id, update_data)
        return self.get_transaction(db, user_id, portfolio_id, transaction_id)

    def delete_transaction(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        transaction_id: UUID,
    ) -> bool:
        self._get_portfolio_for_user(db, user_id, portfolio_id)

        transaction = self.transaction_repository.get_by_id(db, transaction_id)
        if transaction is None or transaction.portfolio_id != portfolio_id:
            raise TransactionNotFoundError(
                f"Transaction {transaction_id} was not found in portfolio {portfolio_id}."
            )

        return self.transaction_repository.delete(db, transaction_id)
