import { useEffect, useState } from 'react'
import { api } from '../api'
import { resources } from './resources'

const pageSize = 10
function ResourceForm({ resource, record, onSaved, onCancel }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const editing = !!record.id
  const fields = resources[resource].fields.filter(([name]) => {
    if (resource === 'applications') return editing ? name === 'status' : name !== 'status'
    return !(resource === 'advertisements' && editing && name === 'company_id')
  })
  async function submit(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const body = Object.fromEntries(fields.map(([name, , type]) => {
      const value = form.get(name)
      return [name, value === '' ? null : ['id', 'number'].includes(type) ? Number(value) : value]
    }))
    setBusy(true); setError('')
    try {
      await api(`/${resource}/${editing ? record.id : ''}`, { method: editing ? 'PATCH' : 'POST', body })
      onSaved()
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }
  return <form className="admin-form" onSubmit={submit}>
    <h2>{editing ? `Modifier #${record.id}` : 'Nouvel enregistrement'}</h2>
    {resource === 'people' && <p>Une fiche personne ne crée pas de mot de passe. Les utilisateurs créent leur compte depuis la page d’inscription.</p>}
    {fields.map(([name, label, type, required, maxLength]) => <label key={name}>{label}
      {Array.isArray(type) ? <select name={name} aria-label={label} defaultValue={record[name] ?? (required ? type[0] : '')} required={required}>
        {!required && <option value="">Non précisé</option>}
        {type.map((value) => <option key={value}>{value}</option>)}
      </select> : type === 'textarea' ? <textarea name={name} defaultValue={record[name] ?? ''} required={required} maxLength={maxLength} rows={3} />
        : <input name={name} type={type === 'id' ? 'number' : type} defaultValue={record[name] ?? ''} required={required} maxLength={maxLength}
          min={type === 'id' ? 1 : type === 'number' ? 0 : undefined} step={type === 'number' ? '0.01' : undefined} />}
    </label>)}
    {error && <p role="alert">{error}</p>}
    <div className="actions"><button disabled={busy}>Enregistrer</button><button type="button" disabled={busy} onClick={onCancel}>Annuler</button></div>
  </form>
}

function ResourcePanel({ resource }) {
  const [rows, setRows] = useState([])
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [record, setRecord] = useState(null)
  const [deleting, setDeleting] = useState(null)
  const [busy, setBusy] = useState(false)
  const [revision, setRevision] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    api(`/${resource}/?offset=${page * pageSize}&limit=${pageSize}`, { signal: controller.signal })
      .then(setRows)
      .catch((err) => { if (err.name !== 'AbortError') setError(err.message) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [resource, page, revision])

  function reload(message = '') {
    setNotice(message); setError(''); setLoading(true); setRevision(revision + 1)
  }
  async function remove() {
    setBusy(true); setError('')
    try {
      await api(`/${resource}/${deleting}`, { method: 'DELETE' })
      setDeleting(null); reload('Enregistrement supprimé.')
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }
  const columns = rows.length ? Object.keys(rows[0]) : []
  return <section>
    <div className="actions"><h2>{resources[resource].label}</h2><button onClick={() => { setRecord({}); setNotice('') }}>Créer</button></div>
    {notice && <p role="status">{notice}</p>}
    {record && <ResourceForm key={record.id || 'new'} resource={resource} record={record} onCancel={() => setRecord(null)} onSaved={() => { setRecord(null); reload('Enregistrement sauvegardé.') }} />}
    {error && <div role="alert"><p>{error}</p><button onClick={() => reload()}>Réessayer</button></div>}
    {deleting !== null && <div className="confirmation">
      <p>Supprimer #{deleting} ? Les annonces ou candidatures liées seront aussi supprimées. Cette action est définitive.</p>
      <button disabled={busy} onClick={remove}>Confirmer la suppression</button>{' '}
      <button disabled={busy} onClick={() => setDeleting(null)}>Annuler</button>
    </div>}
    {loading ? <p role="status">Chargement…</p> : <div className="table-scroll">
      {!rows.length ? <p>Aucun enregistrement sur cette page.</p> : <table>
        <caption>{resources[resource].label} — page {page + 1}</caption>
        <thead><tr>{columns.map((column) => <th key={column} scope="col">{column}</th>)}<th scope="col">Actions</th></tr></thead>
        <tbody>{rows.map((row) => <tr key={row.id}>
          {columns.map((column) => <td key={column}>{String(row[column] ?? '—')}</td>)}
          <td><button onClick={() => setRecord(row)}>Modifier #{row.id}</button> <button onClick={() => setDeleting(row.id)}>Supprimer #{row.id}</button></td>
        </tr>)}</tbody>
      </table>}
    </div>}
    <nav className="pagination" aria-label="Pagination des enregistrements">
      <button disabled={!page || loading} onClick={() => { setLoading(true); setError(''); setPage(page - 1) }}>Précédent</button>
      <span>Page {page + 1}</span>
      <button disabled={loading || !!error || rows.length < pageSize} onClick={() => { setLoading(true); setError(''); setPage(page + 1) }}>Suivant</button>
    </nav>
  </section>
}

export default function Admin() {
  const [resource, setResource] = useState('advertisements')
  return <>
    <h1>Administration</h1>
    <nav className="actions" aria-label="Tables de la base">{Object.entries(resources).map(([key, value]) =>
      <button key={key} aria-pressed={resource === key} onClick={() => setResource(key)}>{value.label}</button>)}</nav>
    <ResourcePanel key={resource} resource={resource} />
  </>
}
