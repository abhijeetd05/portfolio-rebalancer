import { useCallback, useMemo, useState } from 'react'
import { ApiError } from '../api/client'
import { CANONICAL_ASSET_TYPES, createTargetAllocation, deleteTargetAllocation, getTargetAllocations, updateTargetAllocation } from '../api/targetAllocations'
import { usePortfolioResource } from '../hooks/usePortfolioResource'
import type { TargetAllocationRecord } from '../types/portfolio'

interface TargetAllocationProps { portfolioId: string | undefined }

function TargetAllocation({ portfolioId }: TargetAllocationProps) {
  const load = useCallback((id: string) => getTargetAllocations(id), [])
  const { data, loading, error, retry } = usePortfolioResource(portfolioId, load)
  const [showForm, setShowForm] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const allocations = useMemo(() => data ?? [], [data])
  const total = useMemo(() => allocations.reduce((sum, allocation) => sum + Number(allocation.target_percentage), 0), [allocations])
  const availableTypes = CANONICAL_ASSET_TYPES.filter((type) => !allocations.some((allocation) => allocation.asset_type === type))

  function message(errorValue: unknown, action: string) {
    if (errorValue instanceof ApiError && errorValue.status === 409) return 'This change conflicts with the current target allocation. Check for a duplicate asset type or a total above 100%.'
    if (errorValue instanceof ApiError && errorValue.status === 403) return 'You do not have permission to change this portfolio.'
    if (errorValue instanceof ApiError && errorValue.status === 404) return 'This portfolio or target allocation could not be found.'
    if (errorValue instanceof ApiError && errorValue.status === 401) return 'Your session has expired. Please sign in again.'
    return `We could not ${action} the target allocation. Please try again.`
  }

  async function create(payload: { asset_type: typeof CANONICAL_ASSET_TYPES[number]; target_percentage: string }) {
    setSaving(true); setActionError(null)
    try { await createTargetAllocation(portfolioId as string, payload); setShowForm(false); retry() }
    catch (errorValue: unknown) { setActionError(message(errorValue, 'create')) }
    finally { setSaving(false) }
  }
  async function update(targetId: string, targetPercentage: string) {
    setSaving(true); setActionError(null)
    try { await updateTargetAllocation(portfolioId as string, targetId, { target_percentage: targetPercentage }); retry() }
    catch (errorValue: unknown) { setActionError(message(errorValue, 'update')) }
    finally { setSaving(false) }
  }
  async function remove(targetId: string) {
    if (!portfolioId || !window.confirm('Delete this target allocation?')) return
    setSaving(true); setActionError(null)
    try { await deleteTargetAllocation(portfolioId, targetId); retry() }
    catch (errorValue: unknown) { setActionError(message(errorValue, 'delete')) }
    finally { setSaving(false) }
  }

  return (
    <section className="dashboard-page" aria-labelledby="target-allocation-title">
      <div className="page-heading"><p className="eyebrow">Target allocation</p><h1 id="target-allocation-title">Your target allocation</h1><p className="page-description">Set the mix you want your portfolio to work toward.</p></div>
      <section className="list-card" aria-labelledby="allocation-list-title">
        <div className="section-heading"><div><p className="card-label">Portfolio plan</p><h3 id="allocation-list-title">Target mix</h3></div><div className="section-actions"><span className="status-pill status-neutral">{loading ? 'Loading' : allocations.length ? `${allocations.length} targets` : 'Not configured'}</span>{portfolioId && <button className="auth-submit add-holding-button" type="button" disabled={availableTypes.length === 0} onClick={() => { setShowForm((open) => !open); setActionError(null) }}>{showForm ? 'Close' : 'Add allocation'}</button>}</div></div>
        {loading && <div className="page-empty-state"><p className="empty-title">Loading your target allocation…</p></div>}
        {error && <div className="page-empty-state"><p className="empty-title">{error}</p><button className="auth-link" type="button" onClick={retry}>Try again</button></div>}
        {!loading && !error && !portfolioId && <div className="page-empty-state"><p className="empty-title">Choose a portfolio to view its target</p></div>}
        {!loading && !error && portfolioId && <div className="allocation-total"><strong>Total target: {formatPercentage(total)}%</strong><span>{total < 100 ? 'You can leave the remainder unallocated.' : 'Fully allocated.'}</span></div>}
        {!loading && !error && portfolioId && showForm && <AllocationForm availableTypes={availableTypes} total={total} saving={saving} error={actionError} onSubmit={create} />}
        {!loading && !error && portfolioId && allocations.length === 0 && !showForm && <div className="page-empty-state"><p className="empty-title">Your target allocation will appear here</p><p>Configure target allocations to describe how you would like your portfolio distributed.</p></div>}
        {!loading && !error && portfolioId && allocations.length > 0 && <AllocationList allocations={allocations} total={total} saving={saving} error={actionError} onUpdate={update} onDelete={remove} />}
      </section>
    </section>
  )
}

function AllocationList({ allocations, total, saving, error, onUpdate, onDelete }: { allocations: TargetAllocationRecord[]; total: number; saving: boolean; error: string | null; onUpdate: (id: string, percentage: string) => Promise<void>; onDelete: (id: string) => Promise<void> }) {
  return <><div className="allocation-list">{allocations.map((allocation) => <AllocationRow key={allocation.target_id} allocation={allocation} total={total} saving={saving} onUpdate={onUpdate} onDelete={onDelete} />)}</div>{error && <p className="auth-error">{error}</p>}</>
}

function AllocationRow({ allocation, total, saving, onUpdate, onDelete }: { allocation: TargetAllocationRecord; total: number; saving: boolean; onUpdate: (id: string, percentage: string) => Promise<void>; onDelete: (id: string) => Promise<void> }) {
  const [percentage, setPercentage] = useState(String(allocation.target_percentage))
  const attemptedTotal = total - Number(allocation.target_percentage) + Number(percentage)
  return <div className="allocation-row"><div><strong>{allocation.asset_type}</strong><span>{allocation.target_percentage}% target</span></div><div className="allocation-bar"><span style={{ width: `${Math.min(Number(allocation.target_percentage), 100)}%` }} /></div><div className="allocation-actions"><input aria-label={`${allocation.asset_type} target percentage`} type="number" min="0" max="100" step="0.01" value={percentage} onChange={(event) => setPercentage(event.target.value)} /><button className="auth-link" type="button" disabled={saving || !percentage || attemptedTotal > 100} onClick={() => void onUpdate(allocation.target_id, percentage)}>Save</button><button className="auth-link" type="button" disabled={saving} onClick={() => void onDelete(allocation.target_id)}>Delete</button></div>{attemptedTotal > 100 && <small className="auth-error">This change would exceed 100%.</small>}</div>
}

function AllocationForm({ availableTypes, total, saving, error, onSubmit }: { availableTypes: readonly typeof CANONICAL_ASSET_TYPES[number][]; total: number; saving: boolean; error: string | null; onSubmit: (payload: { asset_type: typeof CANONICAL_ASSET_TYPES[number]; target_percentage: string }) => Promise<void> }) {
  const [assetType, setAssetType] = useState<typeof CANONICAL_ASSET_TYPES[number] | ''>('')
  const [percentage, setPercentage] = useState('')
  const attemptedTotal = total + Number(percentage || 0)
  return <form className="holding-form" onSubmit={(event) => { event.preventDefault(); if (assetType && percentage && attemptedTotal <= 100) void onSubmit({ asset_type: assetType, target_percentage: percentage }) }}><label>Asset type<select value={assetType} onChange={(event) => setAssetType(event.target.value as typeof CANONICAL_ASSET_TYPES[number])} required><option value="">Select an asset type</option>{availableTypes.map((type) => <option key={type} value={type}>{type}</option>)}</select></label><label>Target percentage<input type="number" min="0" max="100" step="0.01" value={percentage} onChange={(event) => setPercentage(event.target.value)} required /></label>{attemptedTotal > 100 && <p className="auth-error">This allocation would exceed 100%.</p>}{error && <p className="auth-error">{error}</p>}<button className="auth-submit" type="submit" disabled={saving || !assetType || !percentage || attemptedTotal > 100}>{saving ? 'Saving…' : 'Add allocation'}</button></form>
}

function formatPercentage(value: number) { return Number.isInteger(value) ? String(value) : value.toFixed(2).replace(/\.?0+$/, '') }

export default TargetAllocation
