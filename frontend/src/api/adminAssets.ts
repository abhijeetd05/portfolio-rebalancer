import { getJson, postJson, putJson } from './client'
import type { Asset } from '../types/portfolio'

export interface AdminAssetCreate {
  asset_name: string
  asset_type: string
  asset_subtype?: string
  symbol?: string
  external_provider: string
  external_asset_id: string
  currency: string
  data_source?: string
}

export function getAdminAssets(): Promise<Asset[]> {
  return getJson<Asset[]>('/api/admin/assets')
}

export function createAdminAsset(payload: AdminAssetCreate): Promise<Asset> {
  return postJson<Asset>('/api/admin/assets', payload)
}

export function updateAdminAsset(assetId: string, payload: Partial<AdminAssetCreate> & { is_active?: boolean }): Promise<Asset> {
  return putJson<Asset>(`/api/admin/assets/${assetId}`, payload)
}
