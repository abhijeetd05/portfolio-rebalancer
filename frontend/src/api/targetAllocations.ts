import { deleteJson, getJson, postJson, putJson } from './client'
import type { TargetAllocationRecord } from '../types/portfolio'

export const CANONICAL_ASSET_TYPES = ['Equity', 'Debt', 'Precious Metal', 'Crypto'] as const
export type CanonicalAssetType = typeof CANONICAL_ASSET_TYPES[number]
export interface TargetAllocationCreate { asset_type: CanonicalAssetType; target_percentage: string }
export interface TargetAllocationUpdate { target_percentage: string }

const path = (portfolioId: string) => `/api/users/portfolios/${portfolioId}/target-allocations`

export function getTargetAllocations(portfolioId: string) {
  return getJson<TargetAllocationRecord[]>(path(portfolioId))
}
export function createTargetAllocation(portfolioId: string, payload: TargetAllocationCreate) {
  return postJson<TargetAllocationRecord>(path(portfolioId), payload)
}
export function updateTargetAllocation(portfolioId: string, targetId: string, payload: TargetAllocationUpdate) {
  return putJson<TargetAllocationRecord>(`${path(portfolioId)}/${targetId}`, payload)
}
export function deleteTargetAllocation(portfolioId: string, targetId: string) {
  return deleteJson(`${path(portfolioId)}/${targetId}`)
}
