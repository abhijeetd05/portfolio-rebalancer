import { useCallback, useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { createHolding, deleteHolding, getAssets, getCurrentPrice, getHoldings, resolveAsset, searchAssets } from '../api/holdings'
import type { CurrentPrice } from '../api/holdings'
import type { AssetSearchResult } from '../api/holdings'
import { ApiError } from '../api/client'
import { usePortfolioResource } from '../hooks/usePortfolioResource'
import type { Asset, Holding } from '../types/portfolio'
import { formatMoney, formatNumber } from '../utils/format'

interface HoldingsProps {
  portfolioId: string | undefined
}

function Holdings({ portfolioId }: HoldingsProps) {
  const load = useCallback((id: string) => getHoldings(id), [])
  const { data, loading, error, retry } = usePortfolioResource(portfolioId, load)
  const assetLoad = useCallback(() => getAssets(), [])
  const { data: assets, loading: assetsLoading, error: assetsError } = usePortfolioResource('assets', assetLoad)
  const [showForm, setShowForm] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [prices, setPrices] = useState<Record<string, CurrentPrice>>({})
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  useEffect(() => {
    if (!data?.length) {
      return
    }
    let active = true
    void Promise.all(
      data.map(async (holding) => {
        try {
          return [holding.asset_id, await getCurrentPrice(holding.asset_id)] as const
        } catch {
          return null
        }
      }),
    ).then((entries) => {
      if (active) setPrices(Object.fromEntries(entries.filter((entry): entry is [string, CurrentPrice] => entry !== null)))
    })
    return () => { active = false }
  }, [data])

  async function removeHolding(holdingId: string) {
    if (!portfolioId || !window.confirm('Delete this holding? This will not delete the asset or transaction history.')) return
    setDeletingId(holdingId)
    setDeleteError(null)
    try {
      await deleteHolding(portfolioId, holdingId)
      retry()
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 403) {
        setDeleteError('You do not have permission to delete this holding.')
      } else if (requestError instanceof ApiError && requestError.status === 404) {
        setDeleteError('This holding could not be found. Refresh and try again.')
      } else {
        setDeleteError('We could not delete this holding. Please try again.')
      }
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <section className="dashboard-page" aria-labelledby="holdings-title">
      <div className="page-heading">
        <p className="eyebrow">Holdings</p>
        <h1 id="holdings-title">Your holdings</h1>
        <p className="page-description">See the investments currently held in this portfolio.</p>
      </div>
      <section className="list-card" aria-labelledby="holdings-list-title">
        <div className="section-heading">
          <div>
            <p className="card-label">Portfolio contents</p>
            <h3 id="holdings-list-title">Investments</h3>
          </div>
          <div className="section-actions">
            <span className="status-pill status-neutral">{loading ? 'Loading' : data?.length ? `${data.length} holdings` : 'No holdings yet'}</span>
            {portfolioId && <button className="auth-submit add-holding-button" type="button" onClick={() => { setShowForm((open) => !open); setFormError(null) }}>{showForm ? 'Close' : 'Add holding'}</button>}
          </div>
        </div>
        {showForm && portfolioId && <HoldingForm assetsLoading={assetsLoading} assetsError={assetsError} saving={saving} error={formError} onSubmit={async (payload) => { setSaving(true); setFormError(null); try { await createHolding(portfolioId, payload); setShowForm(false); retry() } catch { setFormError('We could not add this holding. Check the details and try again.') } finally { setSaving(false) } }} />}
        {loading && <div className="page-empty-state"><p className="empty-title">Loading your holdings…</p></div>}
        {error && <div className="page-empty-state"><p className="empty-title">{error}</p><button className="auth-link" type="button" onClick={retry}>Try again</button></div>}
        {!loading && !error && !portfolioId && <div className="page-empty-state"><p className="empty-title">Choose a portfolio to view holdings</p><p>Portfolio data is not configured for this account yet.</p></div>}
        {!loading && !error && portfolioId && data?.length === 0 && <div className="page-empty-state"><p className="empty-title">Your holdings will appear here</p><p>Once investments are added to this portfolio, you will be able to review them here.</p></div>}
        {deleteError && <p className="auth-error">{deleteError}</p>}
        {!loading && !error && data && data.length > 0 && <HoldingsTable holdings={data} assets={assets ?? []} prices={prices} deletingId={deletingId} onDelete={(holdingId) => void removeHolding(holdingId)} />}
      </section>
    </section>
  )
}

function HoldingsTable({ holdings, assets, prices, deletingId, onDelete }: { holdings: Holding[]; assets: Asset[]; prices: Record<string, CurrentPrice>; deletingId: string | null; onDelete: (holdingId: string) => void }) {
  const assetsById = new Map(assets.map((asset) => [asset.asset_id, asset]))
  return <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Asset</th><th>Type</th><th>Units</th><th>Average buy price</th><th>Current price</th><th>Total purchase value</th><th>Purchase date</th><th /></tr></thead><tbody>{holdings.map((holding) => { const asset = assetsById.get(holding.asset_id); const price = prices[holding.asset_id]; return <tr key={holding.holding_id}><td><strong className="table-primary">{asset ? asset.asset_name : 'Asset unavailable'}</strong>{asset?.symbol && <small className="table-secondary">{asset.symbol}</small>}</td><td><span className="type-badge">{asset?.asset_type ?? 'Not available'}</span></td><td>{formatNumber(holding.units, 4)}</td><td>{holding.avg_buy_price == null ? 'Not available' : formatNumber(holding.avg_buy_price)}</td><td>{price ? formatMoney(price.price, price.currency) : <span className="muted-value">Unavailable</span>}</td><td>{holding.avg_buy_price == null ? 'Not available' : formatNumber(multiplyDecimals(holding.units, holding.avg_buy_price))}</td><td>{holding.purchase_date ?? '—'}</td><td><button className="table-action table-action-danger" type="button" disabled={deletingId === holding.holding_id} onClick={() => onDelete(holding.holding_id)}>{deletingId === holding.holding_id ? 'Deleting…' : 'Delete'}</button></td></tr> })}</tbody></table></div>
}

function multiplyDecimals(left: string | number, right: string | number): string {
  const leftText = String(left)
  const rightText = String(right)
  const leftParts = leftText.split('.')
  const rightParts = rightText.split('.')
  const scale = (leftParts[1]?.length ?? 0) + (rightParts[1]?.length ?? 0)
  const product = BigInt((leftParts[0] + (leftParts[1] ?? '')) || '0') * BigInt((rightParts[0] + (rightParts[1] ?? '')) || '0')
  const digits = product.toString().padStart(scale + 1, '0')
  return scale === 0 ? digits : `${digits.slice(0, -scale)}.${digits.slice(-scale)}`
}

function HoldingForm({ assetsLoading, assetsError, saving, error, onSubmit }: { assetsLoading: boolean; assetsError: string | null; saving: boolean; error: string | null; onSubmit: (payload: { asset_id: string; units: string; avg_buy_price?: string; purchase_date?: string }) => Promise<void> }) {
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null)
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<AssetSearchResult[]>([])
  const [pendingResult, setPendingResult] = useState<AssetSearchResult | null>(null)
  const [classificationType, setClassificationType] = useState('')
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const [units, setUnits] = useState('')
  const [avgBuyPrice, setAvgBuyPrice] = useState('')
  const [purchaseDate, setPurchaseDate] = useState('')

  useEffect(() => {
    if (query.trim().length < 2) {
      return
    }
    let active = true
    const timer = window.setTimeout(() => {
      void searchAssets(query.trim()).then((items) => {
        if (active) setResults(items)
      }).catch(() => {
        if (active) setSearchError('We could not search Yahoo Finance right now.')
      }).finally(() => {
        if (active) setSearchLoading(false)
      })
    }, 300)
    return () => {
      active = false
      window.clearTimeout(timer)
    }
  }, [query])

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!selectedAsset) return
    const payload: { asset_id: string; units: string; avg_buy_price?: string; purchase_date?: string } = { asset_id: selectedAsset.asset_id, units }
    if (avgBuyPrice) payload.avg_buy_price = avgBuyPrice
    if (purchaseDate) payload.purchase_date = purchaseDate
    await onSubmit(payload)
  }

  async function choose(result: AssetSearchResult) {
    setSearchError(null)
    if (!result.asset_type) {
      setPendingResult(result)
      setClassificationType('')
      return
    }
    try {
      setSelectedAsset(await resolveAsset(result))
      setQuery('')
      setResults([])
    } catch {
      setSearchError('We could not select that security. Please try again.')
    }
  }

  return <form className="holding-form" onSubmit={submit}><label>Search Yahoo Finance<input value={selectedAsset ? `${selectedAsset.asset_name} (${selectedAsset.external_asset_id})` : query} onChange={(event) => { const value = event.target.value; setSelectedAsset(null); setPendingResult(null); setResults([]); setSearchError(null); setSearchLoading(value.trim().length >= 2); setQuery(value) }} placeholder="Search by company or ticker" required disabled={assetsLoading || Boolean(assetsError)} /></label>{searchLoading && <p>Searching…</p>}{searchError && <p className="auth-error">{searchError}</p>}{results.length > 0 && <div className="data-table-wrap"><table className="data-table"><tbody>{results.map((result) => <tr key={result.ticker}><td><button className="auth-link" type="button" onClick={() => void choose(result)}>{result.name} ({result.ticker})</button></td><td>{result.exchange ?? '—'}</td><td>{result.asset_type ?? 'Unresolved'}{result.category ? ` · ${result.category}` : ''}</td></tr>)}</tbody></table></div>}{pendingResult && <div className="classification-confirmation"><p>Yahoo classification is unresolved for {pendingResult.name}. Confirm the canonical asset type before adding it.</p><select value={classificationType} onChange={(event) => setClassificationType(event.target.value)} required><option value="">Select asset type</option><option value="Equity">Equity</option><option value="Debt">Debt</option><option value="Precious Metal">Precious Metal</option><option value="Crypto">Crypto</option></select><button className="auth-submit" type="button" onClick={() => { const result = pendingResult; if (!result || !classificationType) return; void resolveAsset({ ...result, asset_type: classificationType }).then(setSelectedAsset).then(() => { setPendingResult(null); setQuery(''); setResults([]) }).catch(() => setSearchError('We could not select that security. Please try again.')) }}>Confirm classification</button></div>}{query.trim().length >= 2 && !searchLoading && !searchError && results.length === 0 && !selectedAsset && !pendingResult && <p>No Yahoo Finance securities found.</p>}<label>Units<input type="number" min="0.0001" step="any" value={units} onChange={(event) => setUnits(event.target.value)} required /></label><label>Average buy price<input type="number" min="0" step="any" value={avgBuyPrice} onChange={(event) => setAvgBuyPrice(event.target.value)} /></label><label>Purchase date<input type="date" value={purchaseDate} onChange={(event) => setPurchaseDate(event.target.value)} /></label>{assetsError && <p className="auth-error">{assetsError}</p>}{error && <p className="auth-error">{error}</p>}<button className="auth-submit" type="submit" disabled={saving || assetsLoading || Boolean(assetsError) || !selectedAsset}>{saving ? 'Adding…' : 'Add holding'}</button></form>
}

export default Holdings
