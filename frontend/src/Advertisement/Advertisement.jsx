import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'
import style from './Advertisement.module.css'

const contractLabels = {
  cdi: 'Full-time',
  cdd: 'Fixed-term',
  alternance: 'Work-study',
  stage: 'Internship',
  freelance: 'Freelance',
  interim: 'Interim',
}

function formatSalary(salary) {
  if (salary == null) return 'Not specified'
  return `${Number(salary).toLocaleString('fr-FR')} €`
}

function ApplicationForm({ ad }) {
  const { user } = useAuth()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [sent, setSent] = useState(false)

  async function submit(event) {
    event.preventDefault()
    const body = Object.fromEntries(new FormData(event.currentTarget))
    setBusy(true)
    setError('')
    try {
      await api(`/advertisements/${ad.id}/applications`, { method: 'POST', body })
      setSent(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  if (sent) return <p role="status">Your application is saved and sent to the recruiter.</p>

  return <form onSubmit={submit} className="application-form">
    <p className="eyebrow">Applying to</p>
    <h3>{ad.title}</h3>
    <p className={style.meta}>{ad.company?.name || `Company #${ad.company_id}`}</p>
    {user ? <p>Vous postulez en tant que {user.firstname} {user.lastname}. <Link to="/Account">Modifier mes coordonnées</Link></p> : <>
      <p>Already have an account? <Link to="/Login">Sign in</Link> and your details fill in automatically.</p>
      <label>Full name<input name="firstname" required maxLength={50} autoComplete="given-name" placeholder="First name" /></label>
      <label>Last name<input name="lastname" required maxLength={50} autoComplete="family-name" placeholder="Last name" /></label>
      <label>Email<input name="email" type="email" required maxLength={255} autoComplete="email" /></label>
      <label>Phone<input name="phone" type="tel" maxLength={20} autoComplete="tel" /></label>
    </>}
    <label>Message to the recruiter<textarea name="message" required maxLength={10000} rows={5} /></label>
    {error && <p role="alert">{error}</p>}
    <button disabled={busy}>{busy ? 'Sending…' : 'Send my application'}</button>
  </form>
}

export default function Advertisement({ ad }) {
  const [details, setDetails] = useState(null)
  const [expanded, setExpanded] = useState(false)
  const [applying, setApplying] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const companyName = ad.company?.name || `Company #${ad.company_id}`
  const contract = contractLabels[ad.contract_type] || 'Job offer'

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
    <div className={style.initial} aria-hidden="true">{companyName.charAt(0).toUpperCase()}</div>
    <div className={style.content}>
      <h2 className={style.job_title}>{ad.title}</h2>
      <p className={style.meta}>{companyName} · <time dateTime={ad.created_at}>{new Date(ad.created_at).toLocaleDateString('fr-FR')}</time></p>
      <div className={style.badges}>
        <span className="badge">{contract}</span>
        <span className="badge">{ad.location || 'Location to define'}</span>
        {ad.working_time && <span className="badge">{ad.working_time}</span>}
      </div>
      <p className={style.summary}>{ad.short_description}</p>
      <div className={style.buttons}>
        <button className="secondary" onClick={showDetails} disabled={busy} aria-expanded={expanded} aria-controls={`details-${ad.id}`}>
          {busy ? 'Loading…' : expanded ? 'Show less' : 'Learn more'}
        </button>
        <button disabled={ad.status !== 'published'} onClick={() => setApplying(!applying)} aria-expanded={applying}>{applying ? 'Close form' : 'Apply'}</button>
      </div>
      {error && <p role="alert">{error}</p>}
      {expanded && details && <section id={`details-${ad.id}`} className="details">
        <div className={style.detailGrid}>
          <div>
            <h3>About the role</h3>
            <p className="preserve-lines">{details.full_description}</p>
            <h3>Who we are looking for</h3>
            <p>Curious, rigorous and ready to learn. Motivation matters as much as experience.</p>
          </div>
          <dl>
            <div><dt>Salary</dt><dd>{formatSalary(details.salary)}</dd></div>
            <div><dt>Location</dt><dd>{details.location || 'Not specified'}</dd></div>
            <div><dt>Working time</dt><dd>{details.working_time || 'Not specified'}</dd></div>
            <div><dt>Contract</dt><dd>{contractLabels[details.contract_type] || 'Not specified'}</dd></div>
          </dl>
        </div>
      </section>}
      {applying && <ApplicationForm ad={ad} />}
    </div>
  </article>
}
