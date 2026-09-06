from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.schemas.dashboard import DashboardRebalanceResponse, DashboardResponse
from app.schemas.portfolio import PortfolioResponse
from app.schemas.rebalance import (
    RebalanceActionResponse,
    RebalanceEventResponse,
)
from app.schemas.target_allocation import TargetAllocationResponse
from app.schemas.valuation import PortfolioValuationResponse
from app.services.portfolio_service import PortfolioService
from app.services.rebalance_service import RebalanceService
from app.services.target_allocation_service import TargetAllocationService
from app.services.valuation_service import ValuationService


class DashboardService:
    """Compose existing portfolio data for the read-only dashboard."""

    def __init__(
        self,
        portfolio_service: PortfolioService | None = None,
        valuation_service: ValuationService | None = None,
        target_allocation_service: TargetAllocationService | None = None,
        rebalance_service: RebalanceService | None = None,
    ) -> None:
        self.portfolio_service = portfolio_service or PortfolioService()
        self.valuation_service = valuation_service or ValuationService()
        self.target_allocation_service = (
            target_allocation_service or TargetAllocationService()
        )
        self.rebalance_service = rebalance_service or RebalanceService()

    def get_dashboard(
        self,
        db: Session,
        user_id: UUID,
        portfolio_id: UUID,
    ) -> DashboardResponse:
        portfolio = self.portfolio_service.get_portfolio(
            db,
            user_id,
            portfolio_id,
        )
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
        rebalances = self.rebalance_service.list_rebalances(
            db,
            user_id,
            portfolio_id,
        )

        latest_rebalance = None
        if rebalances:
            latest = max(
                rebalances,
                key=lambda result: result.event.created_at,
            )
            latest_rebalance = DashboardRebalanceResponse(
                event=RebalanceEventResponse.model_validate(latest.event),
                actions=[
                    RebalanceActionResponse.model_validate(action)
                    for action in latest.actions
                ],
            )

        return DashboardResponse(
            portfolio=PortfolioResponse.model_validate(portfolio),
            valuation=PortfolioValuationResponse.model_validate(valuation),
            target_allocations=[
                TargetAllocationResponse.model_validate(target_allocation)
                for target_allocation in target_allocations
            ],
            latest_rebalance=latest_rebalance,
        )
