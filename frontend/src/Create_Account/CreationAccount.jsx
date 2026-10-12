import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'

export default function CreateAccount({ editing = false }) {
  const { user, setUser, login } = useAuth()
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()

  async function submit(event) {
    event.preventDefault()
    const body = Object.fromEntries(new FormData(event.currentTarget))
    body.phone = body.phone || null
    setBusy(true)
    setError('')
    setSuccess('')
    try {
      if (editing) {
        setUser(await api('/auth/me', { method: 'PATCH', body }))
        setSuccess('Your account has been updated.')
      } else {
        await api('/auth/register', { method: 'POST', body })
        await login({ email: body.email, password: body.password })
        navigate('/Annonces')
      }
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
        <h1>{editing ? 'Make updates feel easy.' : 'Make yourself at home.'}</h1>
        <p className="auth-note">One account, and every application is a click away. You can update your details at any time.</p>
        <ul className="check-list">
          <li>Apply without retyping your details</li>
          <li>Keep track of the offers you applied to</li>
          <li>Edit your account whenever you want</li>
        </ul>
      </div>
    </aside>
    <div className="auth-card">
      <p className="eyebrow">{editing ? 'Edit my account' : 'Create account'}</p>
      <h1>About you</h1>
      <form key={editing ? user?.id : 'register'} className="form-grid" onSubmit={submit}>
        <label>First name<input name="firstname" defaultValue={editing ? user?.firstname : ''} required maxLength={50} autoComplete="given-name" /></label>
        <label>Last name<input name="lastname" defaultValue={editing ? user?.lastname : ''} required maxLength={50} autoComplete="family-name" /></label>
        <label>Email<input name="email" type="email" defaultValue={editing ? user?.email : ''} required maxLength={255} autoComplete="email" /></label>
        <label>Phone<input name="phone" type="tel" defaultValue={editing ? user?.phone : ''} maxLength={20} autoComplete="tel" /></label>
        {!editing && <label className="full-width">Password<input name="password" type="password" required minLength={10} maxLength={128} autoComplete="new-password" /></label>}
        {!editing && <label className="full-width" style={{ flexDirection: 'row', alignItems: 'center' }}>
          <input type="checkbox" required style={{ width: 'auto' }} /> I agree that my details are stored to process my applications.
        </label>}
        {error && <p className="full-width" role="alert">{error}</p>}
        {success && <p className="full-width" role="status">{success}</p>}
        <div className="actions full-width">
          <button disabled={busy}>{busy ? 'Saving…' : editing ? 'Save changes' : 'Create my account'}</button>
          {!editing && <Link to="/Login">Already a member? Sign in</Link>}
        </div>
      </form>
    </div>
  </section>
}
