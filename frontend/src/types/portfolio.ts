export interface Portfolio {
  portfolio_id: string
  portfolio_name: string
  base_currency: string
}

export interface Asset {
  asset_id: string
  asset_name: string
  symbol: string | null
  external_provider: string | null
  external_asset_id: string | null
  asset_type: string
  asset_subtype: string | null
  currency: string
  is_active: boolean
}

export interface Holding {
  holding_id: string
  portfolio_id: string
  asset_id: string
  units: string | number
  avg_buy_price: string | number | null
  purchase_date: string | null
  created_at: string
  updated_at: string
}

export interface TargetAllocationRecord {
  target_id: string
  portfolio_id: string
  asset_type: string
  target_percentage: string | number
  created_at: string
  updated_at: string
}

export interface Transaction {
  transaction_id: string
  portfolio_id: string
  asset_id: string
  transaction_type: string
  units: string | number
  price: string | number
  transaction_date: string
  fees: string | number
  notes: string | null
  created_at: string
}

export interface RebalanceEvent {
  rebalance_id: string
  portfolio_id: string
  trigger_type: string
  trigger_date: string
  status: string
  recommended_action: string | null
  reason: string | null
  created_at: string
}

export interface RebalanceAction {
  action_id: string
  rebalance_id: string
  asset_id: string
  action: string
  current_allocation: string | number
  target_allocation: string | number
  recommended_value: string | number
  reason: string | null
}

export interface RebalanceRecord {
  event: RebalanceEvent
  actions: RebalanceAction[]
}
