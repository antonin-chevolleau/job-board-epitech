import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import style from './Advertisement.module.css'

function ApplicationForm({ adId }) {
  const { user } = useAuth()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)
  async function submit(event) {
    event.preventDefault()
    const body = Object.fromEntries(new FormData(event.currentTarget))
    // Authenticated identity comes from the server, never from a client-supplied ID.
    setBusy(true); setError('')
    try {
      await api(`/advertisements/${adId}/applications`, { method: 'POST', body })
      setSent(true)
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }
  if (sent) return <p role="status">Votre candidature a bien été enregistrée.</p>
  return <form onSubmit={submit} className="application-form">
    <h3>Votre candidature</h3>
    {user ? <p>Vous postulez en tant que {user.firstname} {user.lastname} ({user.email}, {user.phone || 'téléphone non renseigné'}). <Link to="/Account">Modifier mes coordonnées</Link></p> : <>
      <p><Link to="/CreateAccount">Créez un compte</Link> pour postuler à plusieurs offres et retrouver vos coordonnées.</p>
      <label>Prénom<input name="firstname" required maxLength={50} autoComplete="given-name" /></label>
      <label>Nom<input name="lastname" required maxLength={50} autoComplete="family-name" /></label>
      <label>Email<input name="email" type="email" required maxLength={255} autoComplete="email" /></label>
      <label>Téléphone<input name="phone" type="tel" maxLength={20} autoComplete="tel" /></label>
    </>}
    <label>Message au recruteur<textarea name="message" required maxLength={10000} rows={5} /></label>
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
    if (expanded) { setExpanded(false); return }
    setBusy(true); setError('')
    try {
      setDetails(await api(`/advertisements/${ad.id}`))
      setExpanded(true)
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }
  return <article className={style.div}>
    <div className="badge">{ad.contract_type?.toUpperCase() || 'Offre d’emploi'}{ad.status !== 'published' && ` · ${ad.status}`}</div>
    <h2 className={style.job_title}>{ad.title}</h2>
    <p>{ad.location || 'Lieu à préciser'} · <time dateTime={ad.created_at}>{new Date(ad.created_at).toLocaleDateString('fr-FR')}</time></p>
    <p>{ad.short_description}</p>
    <div className={style.div_button}>
      <button onClick={showDetails} disabled={busy} aria-expanded={expanded} aria-controls={`details-${ad.id}`}>
        {busy ? 'Chargement…' : expanded ? 'Réduire' : 'En savoir plus'}
      </button>
      <button disabled={ad.status !== 'published'} onClick={() => setApplying(!applying)} aria-expanded={applying}>{applying ? 'Fermer le formulaire' : 'Postuler'}</button>
    </div>
    {error && <p role="alert">{error}</p>}
    {expanded && details && <section id={`details-${ad.id}`} className="details">
      <h3>Description du poste</h3>
      <p className="preserve-lines">{details.full_description}</p>
      <dl>
        <dt>Salaire</dt><dd>{details.salary != null ? `${Number(details.salary).toLocaleString('fr-FR')} €` : 'Non précisé'}</dd>
        <dt>Lieu</dt><dd>{details.location || 'Non précisé'}</dd>
        <dt>Temps de travail</dt><dd>{details.working_time || 'Non précisé'}</dd>
        <dt>Contrat</dt><dd>{details.contract_type?.toUpperCase() || 'Non précisé'}</dd>
      </dl>
    </section>}
    {applying && <ApplicationForm adId={ad.id} />}
  </article>
}
