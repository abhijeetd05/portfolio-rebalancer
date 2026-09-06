import { getJson, postJson } from './client'
import type { Portfolio } from '../types/portfolio'

export interface PortfolioCreatePayload {
  portfolio_name: string
  base_currency: string
}

export function getPortfolios(): Promise<Portfolio[]> {
  return getJson<Portfolio[]>('/api/users/portfolios')
}

export function createPortfolio(payload: PortfolioCreatePayload): Promise<Portfolio> {
  return postJson<Portfolio>('/api/users/portfolios', payload)
}
