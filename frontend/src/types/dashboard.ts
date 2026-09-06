export interface Portfolio {
  portfolio_id: string
  portfolio_name: string
  base_currency: string
}

export interface HoldingValuation {
  asset_type: string
  value: string | number
  allocation_percentage: string | number
}

export interface Valuation {
  total_value: string | number
  holdings: HoldingValuation[]
  asset_class_allocations: HoldingValuation[]
}

export interface TargetAllocation {
  target_id: string
  asset_type: string
  target_percentage: string | number
}

export interface RebalanceEvent {
  status: string
  recommended_action: string | null
  reason: string | null
}

export interface DashboardResponse {
  portfolio: Portfolio
  valuation: Valuation
  target_allocations: TargetAllocation[]
  latest_rebalance: { event: RebalanceEvent } | null
}
