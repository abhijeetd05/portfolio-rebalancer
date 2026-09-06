const navigationItems = [
  { label: 'Dashboard', icon: 'grid' },
  { label: 'Holdings', icon: 'wallet' },
  { label: 'Target Allocation', icon: 'target' },
  { label: 'Transactions', icon: 'receipt' },
  { label: 'Rebalance', icon: 'refresh' },
]

function Icon({ name }: { name: string }) {
  const common = {
    width: 19,
    height: 19,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true,
  }

  switch (name) {
    case 'wallet':
      return <svg {...common}><path d="M3.5 7.5h15a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-15a2 2 0 0 1-2-2v-9a2 2 0 0 1 2-2Z" /><path d="M3.5 7.5V6a2 2 0 0 1 2-2h12" /><path d="M16 13h4.5" /><circle cx="16" cy="13" r=".7" fill="currentColor" /></svg>
    case 'target':
      return <svg {...common}><circle cx="12" cy="12" r="8.5" /><circle cx="12" cy="12" r="4.5" /><circle cx="12" cy="12" r="1" fill="currentColor" /></svg>
    case 'receipt':
      return <svg {...common}><path d="M6 3.5h12v17l-3-2-3 2-3-2-3 2v-17Z" /><path d="M9 8h6M9 12h6M9 16h3" /></svg>
    case 'refresh':
      return <svg {...common}><path d="M20 11a8 8 0 0 0-13.7-5.7L4 7.6" /><path d="M4 4v3.6h3.6" /><path d="M4 13a8 8 0 0 0 13.7 5.7l2.3-2.3" /><path d="M20 20v-3.6h-3.6" /></svg>
    default:
      return <svg {...common}><rect x="4" y="4" width="6" height="6" rx="1" /><rect x="14" y="4" width="6" height="6" rx="1" /><rect x="4" y="14" width="6" height="6" rx="1" /><rect x="14" y="14" width="6" height="6" rx="1" /></svg>
  }
}

interface SidebarProps {
  currentPage: string
  isAdmin: boolean
}

function Sidebar({ currentPage, isAdmin }: SidebarProps) {
  return (
    <aside className="sidebar" aria-label="Primary navigation">
      <div className="brand">
        <span className="brand-mark" aria-hidden="true">PR</span>
        <span className="brand-name">Portfolio Rebalancer</span>
      </div>

      <nav className="sidebar-nav">
        <p className="nav-heading">Your portfolio</p>
        <ul className="nav-list">
          {[...navigationItems, ...(isAdmin ? [{ label: 'Admin Assets', icon: 'target' }] : [])].map((item) => (
            <li key={item.label}>
              <a
                className={`nav-item${item.label.toLowerCase().replaceAll(' ', '-') === currentPage ? ' nav-item-active' : ''}`}
                href={item.label === 'Dashboard' ? '#' : `#${item.label.toLowerCase().replaceAll(' ', '-')}`}
                aria-current={item.label.toLowerCase().replaceAll(' ', '-') === currentPage ? 'page' : undefined}
              >
                <Icon name={item.icon} />
                <span>{item.label}</span>
              </a>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar-footer">
        <div className="help-card">
          <span className="help-icon" aria-hidden="true">?</span>
          <div>
            <strong>Need a hand?</strong>
            <span>We'll keep your portfolio easy to understand.</span>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
