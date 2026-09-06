import { useCallback, useState } from 'react'
import type { FormEvent } from 'react'
import { ApiError } from '../api/client'
import { createTransaction, getAssets, getTransactions } from '../api/transactions'
import { usePortfolioResource } from '../hooks/usePortfolioResource'
import type { Asset, Transaction } from '../types/portfolio'
import { formatNumber } from '../utils/format'

interface TransactionsProps { portfolioId: string | undefined }

function Transactions({ portfolioId }: TransactionsProps) {
  const load = useCallback((id: string) => getTransactions(id), [])
  const { data, loading, error, retry } = usePortfolioResource(portfolioId, load)
  const assetLoad = useCallback(() => getAssets(), [])
  const { data: assets, loading: assetsLoading, error: assetsError } = usePortfolioResource('assets', assetLoad)
  const [showForm, setShowForm] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function submit(payload: { asset_id: string; transaction_type: 'BUY' | 'SELL'; units: string; price: string; transaction_date: string; fees?: string; notes?: string }) {
    if (!portfolioId) return
    setSaving(true); setFormError(null)
    try { await createTransaction(portfolioId, payload); setShowForm(false); retry() }
    catch (requestError: unknown) {
      if (requestError instanceof ApiError && requestError.status === 401) setFormError('Your session has expired. Please sign in again.')
      else if (requestError instanceof ApiError && requestError.status === 403) setFormError('You do not have permission to change this portfolio.')
      else if (requestError instanceof ApiError && requestError.status === 404) setFormError('This portfolio or asset could not be found.')
      else setFormError('We could not add this transaction. Check the details and try again.')
    } finally { setSaving(false) }
  }

  return <section className="dashboard-page" aria-labelledby="transactions-title">
    <div className="page-heading"><p className="eyebrow">Transactions</p><h1 id="transactions-title">Portfolio activity</h1><p className="page-description">Review the activity in your portfolio.</p></div>
    <section className="list-card" aria-labelledby="transactions-list-title">
      <div className="section-heading"><div><p className="card-label">Activity history</p><h3 id="transactions-list-title">Transactions</h3></div><div className="section-actions"><span className="status-pill status-neutral">{loading ? 'Loading' : data?.length ? `${data.length} transactions` : 'No activity yet'}</span>{portfolioId && <button className="auth-submit add-holding-button" type="button" onClick={() => { setShowForm((open) => !open); setFormError(null) }}>{showForm ? 'Close' : 'Add transaction'}</button>}</div></div>
      {showForm && portfolioId && <TransactionForm assets={assets ?? []} assetsLoading={assetsLoading} assetsError={assetsError} saving={saving} error={formError} onSubmit={submit} />}
      {loading && <div className="page-empty-state"><p className="empty-title">Loading your transactions…</p></div>}
      {error && <div className="page-empty-state"><p className="empty-title">{error}</p><button className="auth-link" type="button" onClick={retry}>Try again</button></div>}
      {!loading && !error && !portfolioId && <div className="page-empty-state"><p className="empty-title">Choose a portfolio to view activity</p></div>}
      {!loading && !error && portfolioId && data?.length === 0 && <div className="page-empty-state"><p className="empty-title">Your transactions will appear here</p><p>Once there is activity in this portfolio, you will find the history here.</p></div>}
      {!loading && !error && data && data.length > 0 && <TransactionsTable transactions={data} assets={assets ?? []} />}
    </section>
  </section>
}

function TransactionForm({ assets, assetsLoading, assetsError, saving, error, onSubmit }: { assets: Asset[]; assetsLoading: boolean; assetsError: string | null; saving: boolean; error: string | null; onSubmit: (payload: { asset_id: string; transaction_type: 'BUY' | 'SELL'; units: string; price: string; transaction_date: string; fees?: string; notes?: string }) => Promise<void> }) {
  const [assetId, setAssetId] = useState('')
  const [type, setType] = useState<'BUY' | 'SELL'>('BUY')
  const [units, setUnits] = useState('')
  const [price, setPrice] = useState('')
  const [date, setDate] = useState('')
  const [fees, setFees] = useState('')
  const [notes, setNotes] = useState('')
  function submit(event: FormEvent) {
    event.preventDefault()
    if (!assetId || !units || Number(units) <= 0 || !price || Number(price) <= 0 || !date || (fees && Number(fees) < 0)) return
    void onSubmit({ asset_id: assetId, transaction_type: type, units, price, transaction_date: date, ...(fees ? { fees } : {}), ...(notes.trim() ? { notes: notes.trim() } : {}) })
  }
  return <form className="holding-form" onSubmit={submit}><label>Asset<select value={assetId} onChange={(event) => setAssetId(event.target.value)} required disabled={assetsLoading || Boolean(assetsError) || assets.length === 0}><option value="">{assetsLoading ? 'Loading assets…' : assetsError ? 'Unable to load assets' : assets.length === 0 ? 'No assets are available yet' : 'Select an asset'}</option>{assets.map((asset) => <option key={asset.asset_id} value={asset.asset_id}>{asset.asset_name}{asset.symbol ? ` (${asset.symbol})` : ''}</option>)}</select></label><label>Transaction type<select value={type} onChange={(event) => setType(event.target.value as 'BUY' | 'SELL')}><option value="BUY">BUY</option><option value="SELL">SELL</option></select></label><label>Units<input type="number" min="0.0001" step="any" value={units} onChange={(event) => setUnits(event.target.value)} required /></label><label>Price<input type="number" min="0.0001" step="any" value={price} onChange={(event) => setPrice(event.target.value)} required /></label><label>Transaction date<input type="datetime-local" value={date} onChange={(event) => setDate(event.target.value)} required /></label><label>Fees<input type="number" min="0" step="any" value={fees} onChange={(event) => setFees(event.target.value)} /></label><label>Notes<textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={2} /></label>{assetsError && <p className="auth-error">{assetsError}</p>}{assets.length === 0 && !assetsLoading && !assetsError && <p className="auth-error">No assets are available yet. Ask an administrator to make assets available.</p>}{error && <p className="auth-error">{error}</p>}<button className="auth-submit" type="submit" disabled={saving || assetsLoading || Boolean(assetsError) || assets.length === 0}>{saving ? 'Saving…' : 'Add transaction'}</button></form>
}

function TransactionsTable({ transactions, assets }: { transactions: Transaction[]; assets: Asset[] }) {
  const assetsById = new Map(assets.map((asset) => [asset.asset_id, asset]))
  return <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Date</th><th>Asset</th><th>Type</th><th>Units</th><th>Price</th><th>Fees</th><th>Notes</th></tr></thead><tbody>{transactions.map((transaction) => { const asset = assetsById.get(transaction.asset_id); return <tr key={transaction.transaction_id}><td>{new Date(transaction.transaction_date).toLocaleDateString()}</td><td><strong className="table-primary">{asset?.asset_name ?? 'Asset unavailable'}</strong>{asset?.symbol && <small className="table-secondary">{asset.symbol}</small>}</td><td><span className={`type-badge transaction-badge transaction-${transaction.transaction_type.toLowerCase()}`}>{transaction.transaction_type}</span></td><td>{formatNumber(transaction.units, 4)}</td><td>{formatNumber(transaction.price)}</td><td>{formatNumber(transaction.fees)}</td><td>{transaction.notes ?? '—'}</td></tr> })}</tbody></table></div>
}

export default Transactions
