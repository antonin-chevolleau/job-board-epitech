import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../auth'

export default function Login() {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  async function submit(event) {
    event.preventDefault()
    const body = Object.fromEntries(new FormData(event.currentTarget))
    setBusy(true)
    setError('')
    try {
      const user = await login(body)
      navigate(user.role === 'admin' ? '/Admin' : '/Annonces')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return <section className="auth-layout">
    <aside className="auth-panel">
      <div>
        <p className="eyebrow">tanière</p>
        <h1>Welcome home.</h1>
        <p className="auth-note">Sign in to apply in one click: your details are already waiting for you.</p>
      </div>
      <p className="auth-note">Made with care by Teka, Antonin & Najet</p>
    </aside>
    <div className="auth-card">
      <p className="eyebrow">Sign in</p>
      <h1>Good to see you again.</h1>
      <form onSubmit={submit}>
        <label>Email<input name="email" type="email" autoComplete="email" required /></label>
        <label>Password<input name="password" type="password" autoComplete="current-password" required maxLength={128} /></label>
        <div className="actions">
          <label style={{ flexDirection: 'row', alignItems: 'center', margin: 0 }}>
            <input type="checkbox" style={{ width: 'auto' }} /> Remember me
          </label>
          <a href="#forgot">Forgot password?</a>
        </div>
        {error && <p role="alert">{error}</p>}
        <button disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
      </form>
      <p><span className="eyebrow">new here?</span> <Link to="/CreateAccount">Create an account</Link></p>
      <p className="auth-note">Admins are taken to the administration page, everyone else to the job board.</p>
    </div>
  </section>
}
