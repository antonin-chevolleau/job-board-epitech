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
    setBusy(true)
    setError('')
    setSuccess('')
    try {
      if (editing) {
        setUser(await api('/auth/me', { method: 'PUT', body }))
        setSuccess('Votre compte a été mis à jour.')
      } else {
        await api('/auth/register', { method: 'POST', body })
        await login({ username: body.user_name, password: body.password })
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
        <h1>{editing ? 'Vos coordonnées, toujours à jour.' : 'Faites comme chez vous.'}</h1>
        <p className="auth-note">Un seul compte, et chaque candidature est à un clic. Vos coordonnées restent modifiables à tout moment.</p>
        <ul className="check-list">
          <li>Postulez sans ressaisir vos coordonnées</li>
          <li>Modifiez votre compte quand vous voulez</li>
        </ul>
      </div>
    </aside>
    <div className="auth-card">
      <p className="eyebrow">{editing ? 'Modifier mon compte' : 'Créer un compte'}</p>
      <h1>À propos de vous</h1>
      <form key={editing ? user?.id : 'register'} className="form-grid" onSubmit={submit}>
        <label>Nom d’utilisateur<input name="user_name" pattern="[^@]+" title="Sans @" defaultValue={editing ? user?.user_name : ''} required minLength={3} maxLength={50} autoComplete="username" /></label>
        <label>Prénom<input name="first_name" defaultValue={editing ? user?.first_name : ''} required maxLength={100} autoComplete="given-name" /></label>
        <label>Nom<input name="last_name" defaultValue={editing ? user?.last_name : ''} required maxLength={100} autoComplete="family-name" /></label>
        <label>Email<input name="email" type="email" defaultValue={editing ? user?.email : ''} required maxLength={255} autoComplete="email" /></label>
        <label>Téléphone<input name="phone" type="tel" defaultValue={editing ? user?.phone : ''} required minLength={3} maxLength={20} autoComplete="tel" /></label>
        {!editing && <label className="full-width">Mot de passe (8 caractères minimum)<input name="password" type="password" required minLength={8} maxLength={72} autoComplete="new-password" /></label>}
        {!editing && <label className="full-width" style={{ flexDirection: 'row', alignItems: 'center' }}>
          <input type="checkbox" required style={{ width: 'auto' }} /> J’accepte que mes coordonnées soient conservées pour traiter mes candidatures.
        </label>}
        {error && <p className="full-width" role="alert">{error}</p>}
        {success && <p className="full-width" role="status">{success}</p>}
        <div className="actions full-width">
          <button disabled={busy}>{busy ? 'Enregistrement…' : editing ? 'Enregistrer' : 'Créer mon compte'}</button>
          {!editing && <Link to="/Login">Déjà inscrit ? Se connecter</Link>}
        </div>
      </form>
    </div>
  </section>
}
