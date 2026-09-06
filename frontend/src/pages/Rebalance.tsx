import { useCallback, useState } from 'react'
import { ApiError } from '../api/client'
import { createRebalance, getRebalances } from '../api/rebalance'
import { getAssets } from '../api/holdings'
import { usePortfolioResource } from '../hooks/usePortfolioResource'
import type { Asset, RebalanceRecord } from '../types/portfolio'
import { formatNumber, formatPercent } from '../utils/format'

interface RebalanceProps {
  portfolioId: string | undefined
}

function Rebalance({ portfolioId }: RebalanceProps) {
  const load = useCallback((id: string) => getRebalances(id), [])
  const { data, loading, error, retry } = usePortfolioResource(portfolioId, load)
  const latest = data?.[0]
  const assetLoad = useCallback(() => getAssets(), [])
  const { data: assets } = usePortfolioResource('assets', assetLoad)
  const [generating, setGenerating] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  async function generate() {
    if (!portfolioId) return
    setGenerating(true); setActionError(null)
    try { await createRebalance(portfolioId); retry() }
    catch (requestError: unknown) {
      if (requestError instanceof ApiError && requestError.status === 403) setActionError('You do not have permission to review this portfolio.')
      else if (requestError instanceof ApiError && requestError.status === 404) setActionError('This portfolio could not be found.')
      else if (requestError instanceof ApiError && requestError.status === 400) setActionError(requestError.message)
      else setActionError('We could not generate a rebalance review. Please try again.')
    } finally { setGenerating(false) }
  }

  return (
    <section className="dashboard-page" aria-labelledby="rebalance-page-title">
      <div className="page-heading">
        <p className="eyebrow">Rebalance</p>
        <h1 id="rebalance-page-title">Rebalance your portfolio</h1>
        <p className="page-description">See whether your portfolio has moved away from its target allocation and review any recommended changes.</p>
      </div>
      <div className="detail-grid page-detail-grid">
        <section className="detail-card" aria-labelledby="status-title">
          <div className="section-heading">
            <div>
              <p className="card-label">Current position</p>
              <h3 id="status-title">Rebalance status</h3>
            </div>
            <div className="section-actions"><span className="status-pill status-neutral">{loading ? 'Loading' : latest?.event.status ?? 'No activity'}</span>{portfolioId && <button className="auth-submit add-holding-button" type="button" disabled={generating} onClick={() => void generate()}>{generating ? 'Generating…' : 'Generate review'}</button>}</div>
          </div>
          {loading && <div className="page-empty-state"><p className="empty-title">Loading rebalance information…</p></div>}
          {error && <div className="page-empty-state"><p className="empty-title">{error}</p><button className="auth-link" type="button" onClick={retry}>Try again</button></div>}
          {!loading && !error && !portfolioId && <div className="page-empty-state"><p className="empty-title">Choose a portfolio to review</p><p>Portfolio data is not configured for this account yet.</p></div>}
          {!loading && !error && portfolioId && !latest && <div className="page-empty-state"><p className="empty-title">Nothing to review yet</p><p>Rebalance information will appear once your portfolio and target allocation are ready.</p></div>}
          {!loading && !error && latest && <div className="page-empty-state"><p className="empty-title">{latest.event.recommended_action ?? latest.event.status}</p><p>{latest.event.reason ?? 'Your latest rebalance review is available.'}</p>{latest.actions.length > 0 && <p>{latest.actions.length} recommended action{latest.actions.length === 1 ? '' : 's'}.</p>}<ActionList actions={latest.actions} assets={assets ?? []} /></div>}
          {actionError && <p className="auth-error">{actionError}</p>}
        </section>
        <section className="detail-card" aria-labelledby="history-title">
          <div className="section-heading">
            <div>
              <p className="card-label">Past activity</p>
              <h3 id="history-title">Rebalance history</h3>
            </div>
          </div>
          {!loading && !error && (!data || data.length === 0) && <div className="page-empty-state"><p className="empty-title">No rebalance history yet</p><p>Completed rebalance reviews will be listed here.</p></div>}
          {!loading && !error && data && data.length > 0 && <RebalanceHistory records={data} />}
        </section>
      </div>
    </section>
  )
}

function RebalanceHistory({ records }: { records: RebalanceRecord[] }) {
  return <div className="allocation-list">{records.map((record) => <div className="allocation-row" key={record.event.rebalance_id}><div><strong>{record.event.status}</strong><span>{new Date(record.event.trigger_date).toLocaleDateString()} · {record.event.trigger_type}</span></div><span className="status-pill status-neutral">{record.event.recommended_action ?? 'No action'}</span></div>)}</div>
}

function ActionList({ actions, assets }: { actions: RebalanceRecord['actions']; assets: Asset[] }) {
  const assetById = new Map(assets.map((asset) => [asset.asset_id, asset]))
  return <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Asset</th><th>Action</th><th>Current allocation</th><th>Target allocation</th><th>Recommended value</th><th>Reason</th></tr></thead><tbody>{actions.map((action) => { const asset = assetById.get(action.asset_id); return <tr key={action.action_id}><td><strong className="table-primary">{asset?.asset_name ?? 'Asset unavailable'}</strong><small className="table-secondary">{asset?.asset_type ?? 'Not available'}</small></td><td><span className={`type-badge transaction-badge transaction-${action.action.toLowerCase()}`}>{action.action}</span></td><td>{formatPercent(action.current_allocation)}</td><td>{formatPercent(action.target_allocation)}</td><td>{formatNumber(action.recommended_value)}</td><td>{action.reason ?? '—'}</td></tr> })}</tbody></table></div>
}

export default Rebalance
