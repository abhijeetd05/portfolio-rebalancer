import type { ReactNode } from 'react'
import Header from './Header'
import Sidebar from './Sidebar'

interface LayoutProps {
  children: ReactNode
  currentPage: string
  onLogout: () => void
  portfolios: import('../types/portfolio').Portfolio[]
  activePortfolioId: string | null
  onPortfolioChange: (portfolioId: string) => void
  isAdmin: boolean
}

function Layout({ children, currentPage, onLogout, portfolios, activePortfolioId, onPortfolioChange, isAdmin }: LayoutProps) {
  return (
    <div className="app-shell">
      <Sidebar currentPage={currentPage} isAdmin={isAdmin} />
      <div className="app-content">
        <Header portfolios={portfolios} activePortfolioId={activePortfolioId} onPortfolioChange={onPortfolioChange} onLogout={onLogout} />
        <main className="main-content">{children}</main>
      </div>
    </div>
  )
}

export default Layout
