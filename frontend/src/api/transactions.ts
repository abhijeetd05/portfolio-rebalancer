import { getJson, postJson } from './client'
import type { Transaction } from '../types/portfolio'
import type { Asset } from '../types/portfolio'

export interface TransactionCreatePayload {
  asset_id: string
  transaction_type: 'BUY' | 'SELL'
  units: string
  price: string
  transaction_date: string
  fees?: string
  notes?: string
}

export function getTransactions(portfolioId: string): Promise<Transaction[]> {
  return getJson<Transaction[]>(`/api/users/portfolios/${portfolioId}/transactions`)
}

export function createTransaction(portfolioId: string, payload: TransactionCreatePayload): Promise<Transaction> {
  return postJson<Transaction>(`/api/users/portfolios/${portfolioId}/transactions`, payload)
}

export function getAssets(): Promise<Asset[]> {
  return getJson<Asset[]>('/api/assets')
}
