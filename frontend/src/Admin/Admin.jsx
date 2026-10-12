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
    setBusy(true)
    setError('')
    try {
      await api(`/${resource}/${editing ? record.id : ''}`, { method: editing ? 'PATCH' : 'POST', body })
      onSaved()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return <form className="admin-form" onSubmit={submit}>
    <h2>{editing ? `Edit #${record.id}` : resources[resource].action}</h2>
    {resource === 'people' && <p>A person record does not create a password. Users sign up from the account page.</p>}
    <div className="form-grid">
      {fields.map(([name, label, type, required, maxLength]) => <label key={name} className={type === 'textarea' ? 'full-width' : undefined}>{label}
        {Array.isArray(type) ? <select name={name} aria-label={label} defaultValue={record[name] ?? (required ? type[0] : '')} required={required}>
          {!required && <option value="">Not specified</option>}
          {type.map((value) => <option key={value}>{value}</option>)}
        </select> : type === 'textarea' ? <textarea name={name} defaultValue={record[name] ?? ''} required={required} maxLength={maxLength} rows={3} />
          : <input name={name} type={type === 'id' ? 'number' : type} defaultValue={record[name] ?? ''} required={required} maxLength={maxLength}
            min={type === 'id' ? 1 : type === 'number' ? 0 : undefined} step={type === 'number' ? '0.01' : undefined} />}
      </label>)}
    </div>
    {error && <p role="alert">{error}</p>}
    <div className="actions"><button disabled={busy}>Save changes</button><button className="secondary" type="button" disabled={busy} onClick={onCancel}>Cancel</button></div>
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
      reload('Record deleted.')
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  const columns = rows.length ? Object.keys(rows[0]).filter((column) => column !== 'full_description') : []
  return <section>
    <div className="actions">
      <div>
        <h1>{resources[resource].label}</h1>
        <p>List, create, edit and delete records.</p>
      </div>
      <button onClick={() => { setRecord({}); setNotice('') }}>{resources[resource].action}</button>
    </div>
    {notice && <p role="status">{notice}</p>}
    {record && <ResourceForm key={record.id || 'new'} resource={resource} record={record} onCancel={() => setRecord(null)} onSaved={() => { setRecord(null); reload('Record saved.') }} />}
    {error && <div role="alert"><p>{error}</p><button onClick={() => reload()}>Retry</button></div>}
    {deleting !== null && <div className="confirmation">
      <p>Delete #{deleting}? Linked records may also be deleted. This action is final.</p>
      <button disabled={busy} onClick={remove}>Confirm deletion</button>{' '}
      <button className="secondary" disabled={busy} onClick={() => setDeleting(null)}>Cancel</button>
    </div>}
    {loading ? <p role="status">Loading…</p> : <div className="table-scroll">
      {!rows.length ? <p>No record on this page.</p> : <table>
        <caption>Showing {page * pageSize + 1}–{page * pageSize + rows.length} of {resources[resource].label.toLowerCase()}</caption>
        <thead><tr>{columns.map((column) => <th key={column} scope="col">{column}</th>)}<th scope="col">Actions</th></tr></thead>
        <tbody>{rows.map((row) => <tr key={row.id}>
          {columns.map((column) => <td key={column}>{formatValue(row[column])}</td>)}
          <td><button className="secondary" onClick={() => setRecord(row)}>Edit #{row.id}</button> <button className="secondary" onClick={() => setDeleting(row.id)}>Delete #{row.id}</button></td>
        </tr>)}</tbody>
      </table>}
    </div>}
    <nav className="pagination" aria-label="Pagination des enregistrements">
      <button className="secondary" disabled={!page || loading} onClick={() => { setLoading(true); setError(''); setPage(page - 1) }}>1</button>
      <span>Page {page + 1}</span>
      <button className="secondary" disabled={loading || !!error || rows.length < pageSize} onClick={() => { setLoading(true); setError(''); setPage(page + 1) }}>Next</button>
    </nav>
  </section>
}

export default function Admin() {
  const [resource, setResource] = useState('advertisements')
  return <section className="admin-shell">
    <aside className="admin-sidebar">
      <p className="eyebrow">tanière admin</p>
      <h2>Tables</h2>
      {Object.entries(resources).map(([key, value]) => <button className="secondary" key={key} aria-pressed={resource === key} onClick={() => setResource(key)}>{value.label}</button>)}
    </aside>
    <div className="admin-content">
      <ResourcePanel key={resource} resource={resource} />
    </div>
  </section>
}
