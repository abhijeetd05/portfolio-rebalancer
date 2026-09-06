import { getJson } from './client'
import type { DashboardResponse } from '../types/dashboard'

export function getDashboard(portfolioId: string): Promise<DashboardResponse> {
  return getJson<DashboardResponse>(`/api/users/portfolios/${portfolioId}/dashboard`)
}
