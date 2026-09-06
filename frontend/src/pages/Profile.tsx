import { useCallback } from 'react'
import { getCurrentUser } from '../api/users'
import { usePortfolioResource } from '../hooks/usePortfolioResource'

function Profile({ onUnauthorized }: { onUnauthorized: () => void }) {
  const load = useCallback(() => getCurrentUser(), [])
  const { data: user, loading, error, retry } = usePortfolioResource('current-user', load, onUnauthorized)
  if (loading) return <main className="page-empty-state"><p className="empty-title">Loading your profile…</p></main>
  if (error) return <main className="page-empty-state"><p className="empty-title">{error}</p><button className="auth-link" type="button" onClick={retry}>Try again</button></main>
  return (
    <section className="dashboard-page" aria-labelledby="profile-title">
      <div className="page-heading">
        <p className="eyebrow">Account</p>
        <h1 id="profile-title">Your profile</h1>
        <p className="page-description">Review the account information currently available to this session.</p>
      </div>
      <section className="list-card profile-card" aria-labelledby="profile-details-title">
        <div className="section-heading">
          <div>
            <p className="card-label">Profile details</p>
            <h3 id="profile-details-title">Account information</h3>
          </div>
          <span className="status-pill status-neutral">Read only</span>
        </div>
        <dl className="profile-details">
          <div><dt>Username</dt><dd>{user?.user_name ?? 'Not available'}</dd></div>
          <div><dt>Account status</dt><dd>Authenticated</dd></div>
          <div><dt>Age</dt><dd>{user?.age ?? 'Not provided'}</dd></div>
          <div><dt>Gender</dt><dd>{user?.gender ?? 'Not provided'}</dd></div>
        </dl>
        <p className="profile-note">Profile details are read only in this MVP.</p>
      </section>
    </section>
  )
}

export default Profile
