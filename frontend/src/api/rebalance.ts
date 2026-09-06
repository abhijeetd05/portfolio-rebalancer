import { getJson, postJson } from './client'
import type { RebalanceRecord } from '../types/portfolio'

export function getRebalances(portfolioId: string): Promise<RebalanceRecord[]> {
  return getJson<RebalanceRecord[]>(`/api/users/portfolios/${portfolioId}/rebalances`)
}

export function createRebalance(portfolioId: string): Promise<RebalanceRecord> {
  return postJson<RebalanceRecord>(`/api/users/portfolios/${portfolioId}/rebalances`, {
    trigger_type: 'manual',
    trigger_date: new Date().toISOString(),
  })
}
