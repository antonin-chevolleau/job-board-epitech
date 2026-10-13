import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import style from './Advertisement.module.css'

function formatSalary(salary) {
  if (salary == null) return 'Non précisé'
  return `${Number(salary).toLocaleString('fr-FR')} €`
}

function ApplicationForm({ ad }) {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)

  async function submit(event) {
    event.preventDefault()
    const body = Object.fromEntries(new FormData(event.currentTarget))
    if (!user) body.applicant_name = `${body.first_name} ${body.last_name}`
    delete body.first_name
    delete body.last_name
    setBusy(true)
    setError('')
    try {
      // the API treats an expired token as an anonymous visitor: check the session first
      if (user) await api('/auth/me')
      await api(`/advertisements/${ad.id}/applications`, { method: 'POST', body })
      setSent(true)
    } catch (err) {
      if (user && err.status === 401) navigate('/Login')
      else setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  if (sent) return <p role="status">Votre candidature est enregistrée et transmise au recruteur.</p>

  return <form onSubmit={submit} className="application-form">
    <p className="eyebrow">Candidature</p>
    <h3>{ad.title}</h3>
    <p className={style.meta}>{ad.company.name}</p>
    {user ? <p>Vous postulez en tant que {user.first_name} {user.last_name}. <Link to="/Account">Modifier mes coordonnées</Link></p> : <>
      <p>Déjà un compte ? <Link to="/Login">Connectez-vous</Link> et vos coordonnées seront remplies automatiquement.</p>
      <label>Prénom<input name="first_name" required maxLength={90} autoComplete="given-name" /></label>
      <label>Nom<input name="last_name" required maxLength={90} autoComplete="family-name" /></label>
      <label>Email<input name="applicant_email" type="email" required maxLength={255} autoComplete="email" /></label>
      <label>Téléphone<input name="applicant_phone" type="tel" required minLength={3} maxLength={20} autoComplete="tel" /></label>
    </>}
    <label>Message au recruteur<textarea name="message" required maxLength={5000} rows={5} /></label>
    {error && <p role="alert">{error}</p>}
    <button disabled={busy}>{busy ? 'Envoi…' : 'Envoyer ma candidature'}</button>
  </form>
}

export default function Advertisement({ ad }) {
  const [details, setDetails] = useState(null)
  const [expanded, setExpanded] = useState(false)
  const [applying, setApplying] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function showDetails() {
    if (expanded) {
      setExpanded(false)
      return
    }
    setBusy(true)
    setError('')
    try {
      setDetails(await api(`/advertisements/${ad.id}`))
      setExpanded(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return <article className={style.card}>
    <div className={style.initial} aria-hidden="true">{ad.company.name.charAt(0).toUpperCase()}</div>
    <div className={style.content}>
      <h2 className={style.job_title}>{ad.title}</h2>
      <p className={style.meta}>{ad.company.name} · <time dateTime={ad.created_at}>{new Date(ad.created_at).toLocaleDateString('fr-FR')}</time></p>
      <div className={style.badges}>
        <span className="badge">{ad.contract_type}</span>
        <span className="badge">{ad.location || 'Lieu à définir'}</span>
        {ad.working_time && <span className="badge">{ad.working_time}</span>}
      </div>
      <p className={style.summary}>{ad.short_description}</p>
      <div className={style.buttons}>
        <button className="secondary" onClick={showDetails} disabled={busy} aria-expanded={expanded} aria-controls={`details-${ad.id}`}>
          {busy ? 'Chargement…' : expanded ? 'Voir moins' : 'En savoir plus'}
        </button>
        <button disabled={!ad.is_active} onClick={() => setApplying(!applying)} aria-expanded={applying}>{applying ? 'Fermer le formulaire' : 'Postuler'}</button>
      </div>
      {error && <p role="alert">{error}</p>}
      {expanded && details && <section id={`details-${ad.id}`} className="details">
        <div className={style.detailGrid}>
          <div>
            <h3>Le poste</h3>
            <p className="preserve-lines">{details.full_description}</p>
          </div>
          <dl>
            <div><dt>Salaire</dt><dd>{formatSalary(details.salary)}</dd></div>
            <div><dt>Lieu</dt><dd>{details.location || 'Non précisé'}</dd></div>
            <div><dt>Temps de travail</dt><dd>{details.working_time || 'Non précisé'}</dd></div>
            <div><dt>Contrat</dt><dd>{details.contract_type}</dd></div>
          </dl>
        </div>
      </section>}
      {applying && <ApplicationForm ad={ad} />}
    </div>
  </article>
}
