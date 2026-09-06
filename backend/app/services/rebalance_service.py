from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.engine.rebalance_engine import calculate_rebalance
from app.models.rebalance_action import RebalanceAction
from app.models.rebalance_event import RebalanceEvent
from app.repositories.portfolio_repository import PortfolioRepository
from app.repositories.rebalance_action_repository import RebalanceActionRepository
from app.repositories.rebalance_event_repository import RebalanceEventRepository
from app.schemas.rebalance import RebalanceEventCreate
from app.services.portfolio_service import (
    PortfolioAccessDeniedError,
    PortfolioNotFoundError,
)
from app.services.target_allocation_service import TargetAllocationService
from app.services.valuation_service import ValuationService


class RebalanceCalculationError(ValueError):
    """Raised when an engine recommendation cannot be persisted safely."""


class RebalanceNotFoundError(LookupError):
    """Raised when a rebalance does not exist for the requested portfolio."""


@dataclass(frozen=True)
class RebalanceResult:
    event: RebalanceEvent
    actions: list[RebalanceAction]


class RebalanceService:
    def __init__(
        self,
        portfolio_repository: PortfolioRepository | None = None,
        rebalance_event_repository: RebalanceEventRepository | None = None,
        rebalance_action_repository: RebalanceActionRepository | None = None,
        target_allocation_service: TargetAllocationService | None = None,
        valuation_service: ValuationService | None = None,
    ) -> None:
        self.portfolio_repository = portfolio_repository or PortfolioRepository()
        self.rebalance_event_repository = (
            rebalance_event_repository or RebalanceEventRepository()
        )
        self.rebalance_action_repository = (
            rebalance_action_repository or RebalanceActionRepository()
        )
        self.target_allocation_service = (
            target_allocation_service or TargetAllocationService()
        )
        self.valuation_service = valuation_service or ValuationService()

    def _get_portfolio_for_user(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ):
        portfolio = self.portfolio_repository.get_by_id(db, portfolio_id)
        if portfolio is None:
            raise PortfolioNotFoundError(f"Portfolio {portfolio_id} was not found.")
        if portfolio.user_id != user_id:
            raise PortfolioAccessDeniedError(
                f"Portfolio {portfolio_id} does not belong to user {user_id}."
            )
        return portfolio

    def create_rebalance(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        data: RebalanceEventCreate,
    ) -> RebalanceResult:
        portfolio = self._get_portfolio_for_user(db, user_id, portfolio_id)
        valuation = self.valuation_service.get_portfolio_valuation(
            db,
            user_id,
            portfolio_id,
        )
        target_allocations = self.target_allocation_service.list_target_allocations(
            db,
            user_id,
            portfolio_id,
        )
        calculation = calculate_rebalance(valuation, target_allocations)

        asset_ids_by_type: dict[str, UUID] = {}
        for holding in sorted(
            valuation.holdings,
            key=lambda item: (item.asset_type, str(item.asset_id)),
        ):
            asset_ids_by_type.setdefault(holding.asset_type, holding.asset_id)

        missing_target_messages = [
            (
                f"{deviation.asset_type} has a "
                f"{deviation.target_percentage}% target allocation but no current holding."
            )
            for deviation in calculation.deviations
            if deviation.target_percentage > 0 and deviation.current_percentage == 0
        ]
        event_reason = " ".join(missing_target_messages) or None

        try:
            event = RebalanceEvent(
                portfolio=portfolio,
                trigger_type=data.trigger_type,
                trigger_date=data.trigger_date,
                status="COMPLETED",
                recommended_action=(
                    "REBALANCE" if calculation.trade_recommendations else "HOLD"
                ),
                reason=event_reason,
            )
            event = self.rebalance_event_repository.create(db, event)

            actions: list[RebalanceAction] = []
            deviations_by_type = {
                deviation.asset_type: deviation
                for deviation in calculation.deviations
            }
            for recommendation in calculation.trade_recommendations:
                asset_id = asset_ids_by_type.get(recommendation.asset_type)
                if asset_id is None:
                    continue
                deviation = deviations_by_type[recommendation.asset_type]
                action = RebalanceAction(
                    rebalance_event=event,
                    asset_id=asset_id,
                    action=recommendation.action,
                    current_allocation=deviation.current_percentage,
                    target_allocation=deviation.target_percentage,
                    recommended_value=recommendation.trade_value,
                    reason=None,
                )
                actions.append(self.rebalance_action_repository.create(db, action))
        except Exception:
            db.rollback()
            raise

        return RebalanceResult(event=event, actions=actions)

    def get_rebalance(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
        rebalance_id: UUID,
    ) -> RebalanceResult:
        self._get_portfolio_for_user(db, user_id, portfolio_id)
        event = self.rebalance_event_repository.get_by_id(db, rebalance_id)
        if event is None or event.portfolio_id != portfolio_id:
            raise RebalanceNotFoundError(
                f"Rebalance {rebalance_id} was not found in portfolio {portfolio_id}."
            )
        actions = self.rebalance_action_repository.get_by_rebalance_id(
            db,
            rebalance_id,
        )
        return RebalanceResult(event=event, actions=actions)

    def list_rebalances(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> list[RebalanceResult]:
        self._get_portfolio_for_user(db, user_id, portfolio_id)
        events = self.rebalance_event_repository.get_by_portfolio_id(
            db,
            portfolio_id,
        )
        return [
            RebalanceResult(
                event=event,
                actions=self.rebalance_action_repository.get_by_rebalance_id(
                    db,
                    event.rebalance_id,
                ),
            )
            for event in events
        ]
