import { deleteJson, getJson, postJson } from './client'
import type { Holding } from '../types/portfolio'
import type { Asset } from '../types/portfolio'

export interface HoldingCreatePayload {
  asset_id: string
  units: string
  avg_buy_price?: string
  purchase_date?: string
}

export function getHoldings(portfolioId: string): Promise<Holding[]> {
  return getJson<Holding[]>(`/api/users/portfolios/${portfolioId}/holdings`)
}

export function createHolding(portfolioId: string, payload: HoldingCreatePayload): Promise<Holding> {
  return postJson<Holding>(`/api/users/portfolios/${portfolioId}/holdings`, payload)
}

export function deleteHolding(portfolioId: string, holdingId: string): Promise<void> {
  return deleteJson(`/api/users/portfolios/${portfolioId}/holdings/${holdingId}`)
}

export interface CurrentPrice {
  asset_id: string
  price: string | number
  currency: string
}

export function getCurrentPrice(assetId: string): Promise<CurrentPrice> {
  return getJson<CurrentPrice>(`/api/assets/${assetId}/price/latest`)
}

export function getAssets(): Promise<Asset[]> {
  return getJson<Asset[]>('/api/assets')
}

export interface AssetSearchResult {
  ticker: string
  name: string
  exchange: string | null
  asset_type: string | null
  currency: string | null
  instrument_type?: string | null
  category?: string | null
  classification_status?: string
}

export function searchAssets(query: string): Promise<AssetSearchResult[]> {
  return getJson<AssetSearchResult[]>(`/api/assets/search?q=${encodeURIComponent(query)}`)
}

export function resolveAsset(result: AssetSearchResult): Promise<Asset> {
  return postJson<Asset>('/api/assets/resolve', {
    provider: 'yahoo_finance',
    ticker: result.ticker,
    name: result.name,
    exchange: result.exchange,
    asset_type: result.asset_type,
    currency: result.currency,
      category: result.category,
  })
}
