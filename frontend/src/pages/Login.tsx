import { useState } from 'react'
import type { FormEvent } from 'react'
import { login } from '../api/auth'

interface LoginProps {
  onLogin: (token: string, userName: string) => void
  onCreateAccount: () => void
}

function Login({ onLogin, onCreateAccount }: LoginProps) {
  const [userName, setUserName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      const result = await login(userName, password)
      onLogin(result.access_token, userName)
    } catch {
      setError('We could not sign you in. Check your details and try again.')
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">Portfolio Rebalancer</p>
        <h1>Welcome back</h1>
        <p className="page-description">Sign in to view your portfolio.</p>
        <label>User name<input value={userName} onChange={(event) => setUserName(event.target.value)} required /></label>
        <label>Password<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        {error && <p className="auth-error">{error}</p>}
        <button className="auth-submit" type="submit">Sign in</button>
        <button className="auth-link" type="button" onClick={onCreateAccount}>Create an account</button>
      </form>
    </main>
  )
}

export default Login
