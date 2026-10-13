import { useEffect, useState } from 'react'
import { api } from '../api'
import { resources } from './resources'

const pageSize = 8
const formatValue = (value) => {
  if (value === null || value === undefined || value === '') return '—'
  if (typeof value === 'object') return value.name || value.email || `#${value.id}`
  return String(value)
}

function ResourceForm({ resource, record, onSaved, onCancel }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const editing = !!record.id
  const fields = resources[resource].fields.map((field) => resource === 'users' && field[0] === 'password' ? [...field.slice(0, 3), !editing, ...field.slice(4)] : field)

  async function submit(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const body = Object.fromEntries(fields.map(([name, , type]) => {
      const value = form.get(name)
      if (name === 'is_active') return [name, value === 'true']
      return [name, value === '' ? null : ['id', 'number'].includes(type) ? Number(value) : value]
    }))
    if (editing && 'user_id' in record && !('user_id' in body)) body.user_id = record.user_id
    setBusy(true)
    setError('')
    try {
      await api(`/${resource}${editing ? `/${record.id}` : ''}`, { method: editing ? 'PUT' : 'POST', body })
      onSaved()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return <form className="admin-form" onSubmit={submit}>
    <h2>{editing ? `Modifier #${record.id}` : resources[resource].action}</h2>
    <div className="form-grid">
      {fields.map(([name, label, type, required, maxLength]) => <label key={name} className={type === 'textarea' ? 'full-width' : undefined}>{label}
        {Array.isArray(type) ? <select name={name} aria-label={label} defaultValue={record[name] != null ? String(record[name]) : required ? type[0] : ''} required={required}>
          {!required && <option value="">Non précisé</option>}
          {type.map((value) => <option key={value}>{value}</option>)}
        </select> : type === 'textarea' ? <textarea name={name} defaultValue={record[name] ?? ''} required={required} maxLength={maxLength} rows={3} />
          : <input name={name} type={type === 'id' ? 'number' : type} defaultValue={name === 'password' ? '' : record[name] ?? ''} minLength={name === 'password' ? 8 : undefined} required={required} maxLength={maxLength}
            min={type === 'id' ? 1 : type === 'number' ? 0 : undefined} step={type === 'number' ? '0.01' : undefined} />}
      </label>)}
    </div>
    {error && <p role="alert">{error}</p>}
    <div className="actions"><button disabled={busy}>Enregistrer</button><button className="secondary" type="button" disabled={busy} onClick={onCancel}>Annuler</button></div>
  </form>
}

function ResourcePanel({ resource }) {
  const [rows, setRows] = useState([])
  const [total, setTotal] = useState(0)
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
    api(`/${resource}?page=${page + 1}&limit=${pageSize}`, { signal: controller.signal })
      .then((data) => { setRows(data.items); setTotal(data.total) })
      .catch((err) => { if (err.name !== 'AbortError') setError(err.message) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [resource, page, revision])

  function reload(message = '') {
    setNotice(message)
    setError('')
    setLoading(true)
    setRevision(revision + 1)
  }

  async function remove() {
    setBusy(true)
    setError('')
    try {
      await api(`/${resource}/${deleting}`, { method: 'DELETE' })
      setDeleting(null)
      reload('Enregistrement supprimé.')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function edit(row) {
    setNotice('')
    setError('')
    try {
      // the advertisement list only returns a summary: load the full record for a full replacement
      setRecord(resource === 'advertisements' ? await api(`/advertisements/${row.id}`) : row)
    } catch (err) {
      setError(err.message)
    }
  }

  const columns = rows.reduce((names, row) => {
    Object.keys(row).forEach((column) => {
      if (column !== 'full_description' && !names.includes(column)) names.push(column)
    })
    return names
  }, [])
  return <section className="resource-panel">
    <header className="resource-header">
      <div>
        <p className="eyebrow">Administration · {resource}</p>
        <h1>{resources[resource].label}</h1>
        <p className="resource-description">Gérer, créer et modifier : {resources[resource].label.toLowerCase()}.</p>
      </div>
      <button onClick={() => { setRecord({}); setNotice('') }}>{resources[resource].action}</button>
    </header>
    {notice && <p role="status">{notice}</p>}
    {record && <ResourceForm key={record.id || 'new'} resource={resource} record={record} onCancel={() => setRecord(null)} onSaved={() => { setRecord(null); reload('Enregistrement sauvegardé.') }} />}
    {error && <div role="alert"><p>{error}</p><button type="button" onClick={() => reload()}>Réessayer</button></div>}
    {deleting !== null && <div className="confirmation">
      <p>Supprimer #{deleting} ? Les enregistrements liés peuvent aussi être supprimés. Cette action est définitive.</p>
      <div className="confirmation-actions">
        <button type="button" disabled={busy} onClick={remove}>Confirmer la suppression</button>
        <button className="secondary" type="button" disabled={busy} onClick={() => setDeleting(null)}>Annuler</button>
      </div>
    </div>}
    {loading ? <p role="status">Chargement…</p> : <div className="table-scroll" tabIndex="0" aria-label={`Tableau défilant : ${resources[resource].label.toLowerCase()}`}>
      {!rows.length ? <p className="empty-state">Aucun enregistrement sur cette page.</p> : <table className="admin-table">
        <caption>
          {resources[resource].label} {page * pageSize + 1}–{page * pageSize + rows.length} sur {total}
        </caption>
        <thead>
          <tr>
            {columns.map((column) => <th key={column} scope="col" className={`column-${column}`}>{column.replaceAll('_', ' ')}</th>)}
            <th scope="col" className="actions-column">Actions</th>
          </tr>
        </thead>
        <tbody>{rows.map((row) => <tr key={row.id}>
          {columns.map((column) => {
            const value = formatValue(row[column])
            return <td key={column} className={`column-${column}`} data-label={column.replaceAll('_', ' ')} title={value}>{value}</td>
          })}
          <td className="table-actions" data-label="Actions">
            <button type="button" className="secondary" aria-label={`Modifier ${resources[resource].label.toLowerCase()} #${row.id}`} onClick={() => edit(row)}>Modifier</button>
            <button type="button" className="secondary" aria-label={`Supprimer ${resources[resource].label.toLowerCase()} #${row.id}`} onClick={() => setDeleting(row.id)}>Supprimer</button>
          </td>
        </tr>)}</tbody>
      </table>}
    </div>}
    <nav className="pagination" aria-label="Pagination des enregistrements">
      <button type="button" className="secondary" disabled={!page || loading} onClick={() => { setLoading(true); setError(''); setPage(page - 1) }}>Précédent</button>
      <span>Page {page + 1} / {Math.max(1, Math.ceil(total / pageSize))}</span>
      <button type="button" className="secondary" disabled={loading || !!error || (page + 1) * pageSize >= total} onClick={() => { setLoading(true); setError(''); setPage(page + 1) }}>Suivant</button>
    </nav>
  </section>
}

export default function Admin() {
  const [resource, setResource] = useState('advertisements')
  return <section className="admin-page">
    <header className="admin-page-header">
      <div>
        <p className="eyebrow">tanière admin</p>
        <h1>Espace de travail</h1>
        <p>Gérez le job board depuis un seul espace clair.</p>
      </div>
      <span className="admin-badge">Administrateur</span>
    </header>
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-heading">
          <p className="eyebrow">Navigation</p>
          <h2>Ressources</h2>
        </div>
        <nav className="admin-resource-nav" aria-label="Ressources d’administration">
          {Object.entries(resources).map(([key, value]) => <button type="button" className="secondary" key={key} aria-pressed={resource === key} onClick={() => setResource(key)}>{value.label}</button>)}
        </nav>
      </aside>
      <main className="admin-content">
        <ResourcePanel key={resource} resource={resource} />
      </main>
    </div>
  </section>
}
