import './App.css'
import { useCallback, useEffect, useState } from 'react'
import { getDashboard } from './api/dashboard'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import type { DashboardResponse } from './types/dashboard'
import Holdings from './pages/Holdings'
import TargetAllocation from './pages/TargetAllocation'
import Transactions from './pages/Transactions'
import Rebalance from './pages/Rebalance'
import Login from './pages/Login'
import Register from './pages/Register'
import CreatePortfolio from './pages/CreatePortfolio'
import { getPortfolios } from './api/portfolios'
import type { Portfolio } from './types/portfolio'
import { getAdminAssets } from './api/adminAssets'
import AdminAssets from './pages/AdminAssets'
import Profile from './pages/Profile'
import { ApiError } from './api/client'

function App() {
  const [currentPage, setCurrentPage] = useState(() => window.location.hash.slice(1) || 'dashboard')
  const [token, setToken] = useState(() => localStorage.getItem('access_token'))
  const [showRegister, setShowRegister] = useState(false)
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [portfolios, setPortfolios] = useState<Portfolio[]>([])
  const [portfoliosLoading, setPortfoliosLoading] = useState(false)
  const [portfolioError, setPortfolioError] = useState<string | null>(null)
  const [activePortfolioId, setActivePortfolioId] = useState<string | null>(null)
  const [portfolioSelectionReady, setPortfolioSelectionReady] = useState(false)
  const [portfolioAttempt, setPortfolioAttempt] = useState(0)
  const [isAdmin, setIsAdmin] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const portfolioId = activePortfolioId ?? undefined

  const clearSession = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('active_portfolio_id')
    localStorage.removeItem('profile_user_name')
    setToken(null)
    setPortfolioSelectionReady(false)
  }, [])

  useEffect(() => {
    const onHashChange = () => setCurrentPage(window.location.hash.slice(1) || 'dashboard')
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  useEffect(() => {
    if (!token) return
    if (!portfolioSelectionReady || !portfolioId || portfoliosLoading || !portfolios.some((portfolio) => portfolio.portfolio_id === portfolioId)) return
    const id = portfolioId
    let active = true
    async function loadDashboard() {
      setDashboard(null)
      setError(null)
      try {
        const result = await getDashboard(id)
        if (active) setDashboard(result)
      } catch (requestError) {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 401) {
          clearSession()
          return
        }
        if (requestError instanceof ApiError && requestError.status === 403) {
          setError('You do not have permission to view this portfolio.')
          return
        }
        if (requestError instanceof ApiError && requestError.status === 404) {
          setError('Current valuation is unavailable because market price data is missing for one or more holdings.')
          return
        }
        if (requestError instanceof ApiError && requestError.status === 400) {
          setError(requestError.message)
          return
        }
        setError('We could not load your portfolio right now. Please try again later.')
      }
    }
    void loadDashboard()
    return () => { active = false }
  }, [clearSession, portfolioId, portfolios, portfoliosLoading, portfolioSelectionReady, token])

  useEffect(() => {
    if (!token) return
    let active = true
    async function loadPortfolios() {
      setPortfoliosLoading(true)
      setPortfolioSelectionReady(false)
      setPortfolioError(null)
      try {
        const result = await getPortfolios()
        if (!active) return
        setPortfolios(result)
            const storedId = localStorage.getItem('active_portfolio_id')
            const stored = result.find((portfolio) => portfolio.portfolio_id === storedId)
        const selected = stored?.portfolio_id ?? result[0]?.portfolio_id ?? null
        setActivePortfolioId(selected)
        if (selected) localStorage.setItem('active_portfolio_id', selected)
        else localStorage.removeItem('active_portfolio_id')
        setPortfolioSelectionReady(true)
      } catch (requestError) {
        if (requestError instanceof ApiError && requestError.status === 401) {
          clearSession()
          return
        }
        if (active) {
          setPortfolioSelectionReady(false)
          setPortfolioError('We could not load your portfolios. Please try again.')
        }
      } finally {
        if (active) setPortfoliosLoading(false)
      }
    }
    void loadPortfolios()
    return () => { active = false }
  }, [clearSession, portfolioAttempt, token])

  useEffect(() => {
    if (!token) return
    getAdminAssets()
      .then(() => setIsAdmin(true))
      .catch((requestError) => {
        if (requestError instanceof ApiError && requestError.status === 401) {
          clearSession()
          return
        }
        setIsAdmin(false)
      })
  }, [clearSession, token])

  if (!token) {
    return showRegister
      ? <Register onRegistered={() => setShowRegister(false)} onBack={() => setShowRegister(false)} />
      : <Login onLogin={(value, name) => { localStorage.setItem('access_token', value); localStorage.setItem('profile_user_name', name); setToken(value) }} onCreateAccount={() => setShowRegister(true)} />
  }

  if (portfoliosLoading) return <main className="auth-page"><p className="empty-title">Loading your portfolios…</p></main>
  if (portfolioError) return <main className="auth-page"><div className="auth-card"><p className="auth-error">{portfolioError}</p><button className="auth-submit" type="button" onClick={() => setPortfolioAttempt((attempt) => attempt + 1)}>Try again</button></div></main>
  if (portfolios.length === 0) return <CreatePortfolio onCreated={(portfolio) => { setPortfolios([portfolio]); setActivePortfolioId(portfolio.portfolio_id); localStorage.setItem('active_portfolio_id', portfolio.portfolio_id) }} />

  return (
    <Layout currentPage={currentPage} isAdmin={isAdmin} portfolios={portfolios} activePortfolioId={activePortfolioId} onPortfolioChange={(id) => { setActivePortfolioId(id); localStorage.setItem('active_portfolio_id', id) }} onLogout={clearSession}>
      {currentPage === 'admin-assets' && isAdmin ? <AdminAssets /> :
        currentPage === 'holdings' ? <Holdings portfolioId={portfolioId} /> :
        currentPage === 'profile' ? <Profile onUnauthorized={clearSession} /> :
          currentPage === 'target-allocation' ? <TargetAllocation key={portfolioId ?? 'no-portfolio'} portfolioId={portfolioId} /> :
          currentPage === 'transactions' ? <Transactions portfolioId={portfolioId} /> :
            currentPage === 'rebalance' ? <Rebalance portfolioId={portfolioId} /> :
              <Dashboard dashboard={dashboard} loading={Boolean(portfolioId) && !dashboard && !error} error={error} />}
    </Layout>
  )
}

export default App
