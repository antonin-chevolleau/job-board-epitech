import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../auth'
import style from './Login.module.css'

export default function Login() {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()
  async function submit(event) {
    event.preventDefault()
    const body = Object.fromEntries(new FormData(event.currentTarget))
    setBusy(true); setError('')
    try {
      const user = await login(body)
      navigate(user.role === 'admin' ? '/Admin' : '/Annonces')
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }
  return <section className={style.div}>
    <h1>Connexion</h1>
    <form className={style.form} onSubmit={submit}>
      <label>Email<input name="email" type="email" autoComplete="email" required /></label>
      <label>Mot de passe<input name="password" type="password" autoComplete="current-password" required maxLength={128} /></label>
      {error && <p role="alert">{error}</p>}
      <button disabled={busy}>{busy ? 'Connexion…' : 'Se connecter'}</button>
    </form>
    <Link to="/CreateAccount">Créer un compte</Link>
  </section>
}
