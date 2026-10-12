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
        <p className="resource-description">Manage, create and update {resources[resource].label.toLowerCase()}.</p>
      </div>
      <button onClick={() => { setRecord({}); setNotice('') }}>{resources[resource].action}</button>
    </header>
    {notice && <p role="status">{notice}</p>}
    {record && <ResourceForm key={record.id || 'new'} resource={resource} record={record} onCancel={() => setRecord(null)} onSaved={() => { setRecord(null); reload('Record saved.') }} />}
    {error && <div role="alert"><p>{error}</p><button type="button" onClick={() => reload()}>Retry</button></div>}
    {deleting !== null && <div className="confirmation">
      <p>Delete #{deleting}? Linked records may also be deleted. This action is final.</p>
      <div className="confirmation-actions">
        <button type="button" disabled={busy} onClick={remove}>Confirm deletion</button>
        <button className="secondary" type="button" disabled={busy} onClick={() => setDeleting(null)}>Cancel</button>
      </div>
    </div>}
    {loading ? <p role="status">Loading…</p> : <div className="table-scroll" tabIndex="0" aria-label={`Scrollable ${resources[resource].label.toLowerCase()} table`}>
      {!rows.length ? <p className="empty-state">No record on this page.</p> : <table className="admin-table">
        <caption>
          Showing {page * pageSize + 1}–{page * pageSize + rows.length} of {resources[resource].label.toLowerCase()}, page {page + 1}
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
            <button type="button" className="secondary" aria-label={`Edit ${resources[resource].label.toLowerCase()} #${row.id}`} onClick={() => setRecord(row)}>Edit</button>
            <button type="button" className="secondary" aria-label={`Delete ${resources[resource].label.toLowerCase()} #${row.id}`} onClick={() => setDeleting(row.id)}>Delete</button>
          </td>
        </tr>)}</tbody>
      </table>}
    </div>}
    <nav className="pagination" aria-label="Pagination des enregistrements">
      <button type="button" className="secondary" disabled={!page || loading} onClick={() => { setLoading(true); setError(''); setPage(page - 1) }}>Previous</button>
      <span>Page {page + 1}</span>
      <button type="button" className="secondary" disabled={loading || !!error || rows.length < pageSize} onClick={() => { setLoading(true); setError(''); setPage(page + 1) }}>Next</button>
    </nav>
  </section>
}

export default function Admin() {
  const [resource, setResource] = useState('advertisements')
  return <section className="admin-page">
    <header className="admin-page-header">
      <div>
        <p className="eyebrow">tanière admin</p>
        <h1>Workspace</h1>
        <p>Manage the job board from one clear and responsive workspace.</p>
      </div>
      <span className="admin-badge">Administrator</span>
    </header>
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-heading">
          <p className="eyebrow">Navigation</p>
          <h2>Resources</h2>
        </div>
        <nav className="admin-resource-nav" aria-label="Admin resources">
          {Object.entries(resources).map(([key, value]) => <button type="button" className="secondary" key={key} aria-pressed={resource === key} onClick={() => setResource(key)}>{value.label}</button>)}
        </nav>
      </aside>
      <main className="admin-content">
        <ResourcePanel key={resource} resource={resource} />
      </main>
    </div>
  </section>
}
