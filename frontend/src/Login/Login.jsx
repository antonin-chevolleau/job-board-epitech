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
        <h1>Bienvenue chez vous.</h1>
        <p className="auth-note">Connectez-vous pour postuler en un clic : vos coordonnées vous attendent déjà.</p>
      </div>
      <p className="auth-note">Fait avec soin par Teka, Antonin & Najet</p>
    </aside>
    <div className="auth-card">
      <p className="eyebrow">Connexion</p>
      <h1>Content de vous revoir.</h1>
      <form onSubmit={submit}>
        <label>Nom d’utilisateur ou email<input name="username" autoComplete="username" required /></label>
        <label>Mot de passe<input name="password" type="password" autoComplete="current-password" required maxLength={72} /></label>
        {error && <p role="alert">{error}</p>}
        <button disabled={busy}>{busy ? 'Connexion…' : 'Se connecter'}</button>
      </form>
      <p><span className="eyebrow">nouveau ici ?</span> <Link to="/CreateAccount">Créer un compte</Link></p>
      <p className="auth-note">Les administrateurs arrivent sur la page d’administration, les autres sur les offres.</p>
    </div>
  </section>
}
