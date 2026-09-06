import { useState } from 'react'
import type { Portfolio } from '../types/portfolio'

interface HeaderProps {
  onLogout: () => void
  portfolios: Portfolio[]
  activePortfolioId: string | null
  onPortfolioChange: (portfolioId: string) => void
}

function Header({ onLogout, portfolios, activePortfolioId, onPortfolioChange }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [confirmingLogout, setConfirmingLogout] = useState(false)

  return (
    <header className="top-bar">
      <div className="top-bar-context">
        <span className="top-bar-dot" aria-hidden="true" />
        {portfolios.length > 1 ? <label className="portfolio-selector">Portfolio
          <select value={activePortfolioId ?? ''} onChange={(event) => onPortfolioChange(event.target.value)} aria-label="Select portfolio">
            {portfolios.map((portfolio) => <option key={portfolio.portfolio_id} value={portfolio.portfolio_id}>{portfolio.portfolio_name}</option>)}
          </select>
        </label> : <span>{portfolios[0]?.portfolio_name ?? 'Portfolio workspace'}</span>}
      </div>

      <div className="account-menu">
        <button className="account-button" type="button" aria-label="Open account menu" aria-expanded={menuOpen} aria-haspopup="menu" onClick={() => { setMenuOpen((open) => !open); setConfirmingLogout(false) }}>
          <span className="user-avatar" aria-hidden="true">U</span>
          <span className="account-label">Account</span>
          <svg className="chevron" viewBox="0 0 20 20" fill="none" aria-hidden="true">
            <path d="m6 8 4 4 4-4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </button>
        {menuOpen && <div className="account-dropdown" role="menu" aria-label="Account options">
          {!confirmingLogout ? <><a className="account-menu-item" role="menuitem" href="#profile" onClick={() => setMenuOpen(false)}>Profile</a><button className="account-menu-item" type="button" role="menuitem" onClick={() => setConfirmingLogout(true)}>Log out</button></> : <div className="logout-confirmation" role="alertdialog" aria-label="Confirm logout">
            <p>Log out of your account?</p>
            <div><button className="account-menu-item" type="button" onClick={onLogout}>Log out</button><button className="account-menu-cancel" type="button" onClick={() => setConfirmingLogout(false)}>Cancel</button></div>
          </div>}
        </div>}
      </div>
    </header>
  )
}

export default Header
