import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'
import { createAdminAsset, getAdminAssets, updateAdminAsset } from '../api/adminAssets'
import { usePortfolioResource } from '../hooks/usePortfolioResource'
import type { Asset } from '../types/portfolio'

function AdminAssets() {
  const load = useCallback(() => getAdminAssets(), [])
  const { data, loading, error, retry } = usePortfolioResource('admin-assets', load)
  const [showForm, setShowForm] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function submit(payload: { asset_name: string; asset_type: string; currency: string; symbol?: string; external_provider: string; external_asset_id: string }) {
    setSaving(true); setFormError(null)
    try { await createAdminAsset(payload); setShowForm(false); retry() } catch { setFormError('We could not create this asset. Check the details and try again.') } finally { setSaving(false) }
  }

  return <section className="dashboard-page" aria-labelledby="admin-assets-title"><div className="page-heading"><p className="eyebrow">Administration</p><h1 id="admin-assets-title">Assets</h1><p className="page-description">Manage the assets available for portfolio holdings.</p></div><section className="list-card"><div className="section-heading"><h3>Available assets</h3><button className="auth-submit add-holding-button" type="button" onClick={() => setShowForm((open) => !open)}>{showForm ? 'Close' : 'Add asset'}</button></div>{showForm && <AssetForm saving={saving} error={formError} onSubmit={submit} />}{loading && <div className="page-empty-state"><p className="empty-title">Loading assets…</p></div>}{error && <div className="page-empty-state"><p className="empty-title">{error}</p><button className="auth-link" type="button" onClick={retry}>Try again</button></div>}{!loading && !error && data?.length === 0 && <div className="page-empty-state"><p className="empty-title">No assets yet</p><p>Create an asset to make it available to users.</p></div>}{!loading && !error && data && data.length > 0 && <AdminAssetTable assets={data} onUpdated={retry} />}</section></section>
}

function AssetForm({ saving, error, onSubmit }: { saving: boolean; error: string | null; onSubmit: (payload: { asset_name: string; asset_type: string; currency: string; symbol?: string; external_provider: string; external_asset_id: string }) => Promise<void> }) {
  const [name, setName] = useState(''); const [type, setType] = useState(''); const [currency, setCurrency] = useState('INR'); const [symbol, setSymbol] = useState(''); const [externalId, setExternalId] = useState('')
  function submit(event: FormEvent) { event.preventDefault(); void onSubmit({ asset_name: name.trim(), asset_type: type.trim(), currency: currency.toUpperCase(), external_provider: 'yahoo_finance', external_asset_id: externalId.trim(), ...(symbol.trim() ? { symbol: symbol.trim() } : {}) }) }
  return <form className="holding-form" onSubmit={submit}><label>Asset name<input value={name} onChange={(event) => setName(event.target.value)} required /></label><label>Asset type<select value={type} onChange={(event) => setType(event.target.value)} required><option value="">Select a type</option><option>Equity</option><option>Debt</option><option>Precious Metal</option><option>Crypto</option></select></label><label>Symbol<input value={symbol} onChange={(event) => setSymbol(event.target.value)} /></label><label>Yahoo Finance ticker<input value={externalId} onChange={(event) => setExternalId(event.target.value)} placeholder="e.g. RELIANCE.NS" required /></label><label>Currency<input value={currency} onChange={(event) => setCurrency(event.target.value)} minLength={3} maxLength={3} required /></label>{error && <p className="auth-error">{error}</p>}<button className="auth-submit" type="submit" disabled={saving}>{saving ? 'Creating…' : 'Create asset'}</button></form>
}

function AdminAssetTable({ assets, onUpdated }: { assets: Asset[]; onUpdated: () => void }) {
  const [busy, setBusy] = useState<string | null>(null)
  async function toggle(asset: Asset) { setBusy(asset.asset_id); try { await updateAdminAsset(asset.asset_id, { is_active: !asset.is_active }); onUpdated() } finally { setBusy(null) } }
  return <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Name</th><th>Symbol</th><th>Provider ticker</th><th>Type</th><th>Currency</th><th>Status</th><th /></tr></thead><tbody>{assets.map((asset) => <tr key={asset.asset_id}><td>{asset.asset_name}</td><td>{asset.symbol ?? '—'}</td><td>{asset.external_asset_id ?? '—'}</td><td>{asset.asset_type}</td><td>{asset.currency}</td><td>{asset.is_active ? 'Active' : 'Inactive'}</td><td><button className="auth-link" type="button" disabled={busy === asset.asset_id} onClick={() => void toggle(asset)}>{asset.is_active ? 'Deactivate' : 'Activate'}</button></td></tr>)}</tbody></table></div>
}

export default AdminAssets
