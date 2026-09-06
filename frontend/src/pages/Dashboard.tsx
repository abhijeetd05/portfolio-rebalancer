import type { DashboardResponse, HoldingValuation, TargetAllocation } from '../types/dashboard'
import { formatMoney, formatPercent } from '../utils/format'

interface DashboardProps {
  dashboard: DashboardResponse | null
  loading: boolean
  error: string | null
}

function Dashboard({ dashboard, loading, error }: DashboardProps) {
  if (loading) return <DashboardState title="Loading your portfolio" message="Your portfolio summary will appear here in a moment." />
  if (error) {
    const valuationUnavailable = error.includes('price currency') || error.includes('market price')
    return <DashboardState title={valuationUnavailable ? 'Portfolio valuation is unavailable' : 'We could not load your portfolio'} message={error} />
  }
  if (!dashboard) return <DashboardState title="No portfolio data yet" message="Add holdings and target allocations to start seeing your portfolio summary." />

  const { portfolio, valuation, target_allocations: targets, latest_rebalance: rebalance } = dashboard
  const hasCurrentAllocation = valuation.asset_class_allocations.length > 0
  const hasTargets = targets.length > 0

  return (
    <section className="dashboard-page" aria-labelledby="dashboard-title">
      <div className="welcome-row">
        <div className="page-heading">
          <p className="eyebrow">Overview</p>
          <h1 id="dashboard-title">{portfolio.portfolio_name}</h1>
          <p className="page-description">A clear view of your portfolio value, allocation, and latest rebalance review.</p>
        </div>
        <span className="read-only-note"><span className="note-dot" aria-hidden="true" />Read only</span>
      </div>

      <div className="summary-grid">
        <SummaryCard title="Portfolio value" value={formatMoney(valuation.total_value, portfolio.base_currency)} description="Current value provided by your portfolio valuation." />
        <SummaryCard title="Current allocation" value={hasCurrentAllocation ? `${valuation.asset_class_allocations.length} asset classes` : 'Not available'} description={hasCurrentAllocation ? 'Asset-class values and percentages are shown below.' : 'Add holdings to see your current allocation.'} />
        <SummaryCard title="Target allocation" value={hasTargets ? `${targets.length} targets` : 'Not configured'} description={hasTargets ? 'Your configured target mix is shown below.' : 'Set target allocations to define your portfolio plan.'} />
      </div>

      <div className="dashboard-sections">
        <section className="detail-card dashboard-visual-card" aria-labelledby="allocation-visuals-title">
          <SectionHeading eyebrow="Portfolio mix" title="Allocation visuals" status={hasCurrentAllocation ? 'Current' : 'No holdings'} />
          {hasCurrentAllocation ? <AllocationVisuals current={valuation.asset_class_allocations} targets={targets} /> : <DashboardState title="No allocation to visualize" message="Add holdings to see current allocation visuals." compact />}
        </section>
        <section className="detail-card" aria-labelledby="current-allocation-title">
          <SectionHeading eyebrow="Where your money is" title="Current allocation" status={hasCurrentAllocation ? 'Available' : 'No holdings'} />
          {hasCurrentAllocation ? <AllocationTable rows={valuation.asset_class_allocations} valueLabel="Value" percentageLabel="Current" currency={portfolio.base_currency} /> : <DashboardState title="No portfolio data yet" message="Add holdings to start seeing your current asset-class allocation." compact />}
        </section>
        <section className="detail-card" aria-labelledby="target-allocation-title">
          <SectionHeading eyebrow="Your portfolio plan" title="Target allocation" status={hasTargets ? 'Configured' : 'Not configured'} />
          {hasTargets ? <TargetTable rows={targets} /> : <DashboardState title="No targets configured" message="Configure target allocations when you are ready to set your preferred mix." compact />}
        </section>
      </div>

      <section className="detail-card dashboard-rebalance-card" aria-labelledby="dashboard-rebalance-title">
        <SectionHeading eyebrow="Latest review" title="Rebalance status" status={rebalance?.event.status ?? 'No activity'} />
        <div className="rebalance-empty">
          <div className="rebalance-check" aria-hidden="true">✓</div>
          <div>
            <p className="empty-title">{rebalance?.event.recommended_action ?? 'Nothing to review yet'}</p>
            <p>{rebalance?.event.reason ?? 'A rebalance review will appear when your portfolio has the required data.'}</p>
          </div>
        </div>
        <div className="reassurance"><span aria-hidden="true">i</span><p>Your portfolio will not be changed automatically.</p></div>
      </section>
    </section>
  )
}

const chartColors = ['#5b8c7a', '#6f86ad', '#c49a63', '#9d789d', '#7d9b9b', '#b9786b']

function AllocationVisuals({ current, targets }: { current: HoldingValuation[]; targets: TargetAllocation[] }) {
  const currentByType = new Map(current.map((row) => [row.asset_type, Number(row.allocation_percentage)]))
  const targetByType = new Map(targets.map((row) => [row.asset_type, Number(row.target_percentage)]))
  const types = [...new Set([...currentByType.keys(), ...targetByType.keys()])].sort()
  const segments = current.reduce<string[]>((result, row, index) => {
    const value = Math.max(0, Number(row.allocation_percentage))
    const offset = result.length > 0 ? Number(result[result.length - 1].split(' ').at(-1)?.replace('%', '')) : 0
    result.push(`${chartColors[index % chartColors.length]} ${offset}% ${offset + value}%`)
    return result
  }, [])
  const donutStyle = { background: segments.length > 0 ? `conic-gradient(${segments.join(', ')})` : '#edf1f5' }

  return (
    <div className="allocation-visuals">
      <div className="allocation-donut-wrap">
        <div className="allocation-donut" style={donutStyle} aria-label="Current allocation donut chart">
          <div><strong>{current.length}</strong><span>classes</span></div>
        </div>
        <div className="allocation-legend">
          {current.map((row, index) => <div className="allocation-legend-row" key={row.asset_type}><span className="legend-swatch" style={{ background: chartColors[index % chartColors.length] }} /> <span>{row.asset_type}</span><strong>{formatPercent(row.allocation_percentage)}</strong></div>)}
        </div>
      </div>
      <div className="comparison-bars">
        <div className="comparison-legend"><span><i className="bar-key bar-key-current" />Current</span><span><i className="bar-key bar-key-target" />Target</span></div>
        {types.map((type) => <div className="comparison-row" key={type}><div className="comparison-label"><span>{type}</span><span>{formatPercent(currentByType.get(type) ?? 0)} / {formatPercent(targetByType.get(type) ?? 0)}</span></div><div className="comparison-track"><span className="comparison-bar comparison-bar-current" style={{ width: `${Math.min(100, Math.max(0, currentByType.get(type) ?? 0))}%` }} /><span className="comparison-bar comparison-bar-target" style={{ width: `${Math.min(100, Math.max(0, targetByType.get(type) ?? 0))}%` }} /></div></div>)}
      </div>
    </div>
  )
}

function SummaryCard({ title, value, description }: { title: string; value: string; description: string }) {
  return <article className="summary-card"><div className="summary-card-top"><p className="card-label">{title}</p><span className="summary-icon summary-icon-value" aria-hidden="true">₹</span></div><p className="card-value">{value}</p><p className="card-description">{description}</p></article>
}

function SectionHeading({ eyebrow, title, status }: { eyebrow: string; title: string; status: string }) {
  return <div className="section-heading"><div><p className="card-label">{eyebrow}</p><h3>{title}</h3></div><span className="status-pill status-neutral">{status}</span></div>
}

function AllocationTable({ rows, valueLabel, percentageLabel, currency }: { rows: HoldingValuation[]; valueLabel: string; percentageLabel: string; currency: string }) {
  return <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Asset class</th><th>{valueLabel}</th><th>{percentageLabel}</th></tr></thead><tbody>{rows.map((row) => <tr key={row.asset_type}><td><span className="asset-type-label">{row.asset_type}</span></td><td>{formatMoney(row.value, currency)}</td><td>{formatPercent(row.allocation_percentage)}</td></tr>)}</tbody></table></div>
}

function TargetTable({ rows }: { rows: TargetAllocation[] }) {
  return <div className="data-table-wrap"><table className="data-table"><thead><tr><th>Asset class</th><th>Target</th></tr></thead><tbody>{rows.map((row) => <tr key={row.target_id}><td><span className="asset-type-label">{row.asset_type}</span></td><td>{formatPercent(row.target_percentage)}</td></tr>)}</tbody></table></div>
}

function DashboardState({ title, message, compact = false }: { title: string; message: string; compact?: boolean }) {
  return <div className={compact ? 'dashboard-state dashboard-state-compact' : 'page-empty-state'}><p className="empty-title">{title}</p><p>{message}</p></div>
}

export default Dashboard
