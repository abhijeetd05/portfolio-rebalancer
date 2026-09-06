import { useState } from 'react'
import type { FormEvent } from 'react'
import { register } from '../api/auth'

interface RegisterProps {
  onRegistered: () => void
  onBack: () => void
}

function Register({ onRegistered, onBack }: RegisterProps) {
  const [userName, setUserName] = useState('')
  const [password, setPassword] = useState('')
  const [age, setAge] = useState('')
  const [gender, setGender] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await register(userName, password, age ? Number(age) : undefined, gender || undefined)
      onRegistered()
    } catch {
      setError('We could not create your account. Please check the details and try again.')
    }
  }

  return (
    <main className="auth-page">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">Portfolio Rebalancer</p>
        <h1>Create account</h1>
        <p className="page-description">Create a secure account to get started.</p>
        <label>User name<input value={userName} onChange={(event) => setUserName(event.target.value)} required /></label>
        <label>Password<input type="password" minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        <label>Age (optional)<input type="number" min="1" max="150" value={age} onChange={(event) => setAge(event.target.value)} /></label>
        <label>Gender (optional)<select value={gender} onChange={(event) => setGender(event.target.value)}><option value="">Prefer not to say</option><option value="Female">Female</option><option value="Male">Male</option><option value="Non-binary">Non-binary</option></select></label>
        {error && <p className="auth-error">{error}</p>}
        <button className="auth-submit" type="submit">Create account</button>
        <button className="auth-link" type="button" onClick={onBack}>Back to sign in</button>
      </form>
    </main>
  )
}

export default Register
