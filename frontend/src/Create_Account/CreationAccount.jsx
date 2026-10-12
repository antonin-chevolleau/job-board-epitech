import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import style from './CreateAccount.module.css'

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
    setBusy(true); setError(''); setSuccess('')
    try {
      if (editing) {
        setUser(await api('/auth/me', { method: 'PATCH', body }))
        setSuccess('Votre compte a été mis à jour.')
      } else {
        await api('/auth/register', { method: 'POST', body })
        await login({ email: body.email, password: body.password })
        navigate('/Annonces')
      }
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }
  return <section className={style.div}>
    <h1>{editing ? 'Mon compte' : 'Créer un compte'}</h1>
    <form key={editing ? user?.id : 'register'} className={style.form} onSubmit={submit}>
      <label>Prénom<input name="firstname" defaultValue={editing ? user?.firstname : ''} required maxLength={50} autoComplete="given-name" /></label>
      <label>Nom<input name="lastname" defaultValue={editing ? user?.lastname : ''} required maxLength={50} autoComplete="family-name" /></label>
      <label>Email<input name="email" type="email" defaultValue={editing ? user?.email : ''} required maxLength={255} autoComplete="email" /></label>
      <label>Téléphone<input name="phone" type="tel" defaultValue={editing ? user?.phone : ''} maxLength={20} autoComplete="tel" /></label>
      {!editing && <label>Mot de passe (10 caractères minimum)<input name="password" type="password" required minLength={10} maxLength={128} autoComplete="new-password" /></label>}
      {error && <p role="alert">{error}</p>}
      {success && <p role="status">{success}</p>}
      <button disabled={busy}>{busy ? 'Enregistrement…' : 'Enregistrer'}</button>
    </form>
    {!editing && <Link to="/Login">Déjà un compte ? Se connecter</Link>}
  </section>
}
