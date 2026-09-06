import { useState } from 'react'
import type { FormEvent } from 'react'
import { createPortfolio } from '../api/portfolios'
import type { Portfolio } from '../types/portfolio'

interface CreatePortfolioProps {
  onCreated: (portfolio: Portfolio) => void
}

function CreatePortfolio({ onCreated }: CreatePortfolioProps) {
  const [name, setName] = useState('')
  const [currency, setCurrency] = useState('INR')
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim() || currency.length !== 3) {
      setError('Enter a portfolio name and a three-letter currency code.')
      return
    }
    setSaving(true)
    setError(null)
    try {
      onCreated(await createPortfolio({ portfolio_name: name.trim(), base_currency: currency.toUpperCase() }))
    } catch {
      setError('We could not create your portfolio. Please check the details and try again.')
    } finally {
      setSaving(false)
    }
  }

  return <main className="auth-page"><form className="auth-card" onSubmit={submit}><p className="eyebrow">Portfolio Rebalancer</p><h1>Create your portfolio</h1><p className="page-description">Set up your first portfolio to get started.</p><label>Portfolio name<input value={name} onChange={(event) => setName(event.target.value)} required maxLength={100} /></label><label>Base currency<input value={currency} onChange={(event) => setCurrency(event.target.value.toUpperCase())} required minLength={3} maxLength={3} /></label>{error && <p className="auth-error">{error}</p>}<button className="auth-submit" type="submit" disabled={saving}>{saving ? 'Creating…' : 'Create portfolio'}</button></form></main>
}

export default CreatePortfolio
