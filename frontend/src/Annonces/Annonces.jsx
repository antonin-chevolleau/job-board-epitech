import { useEffect, useMemo, useState } from 'react'
import Advertisement from '../Advertisement/Advertisement.jsx'
import { api } from '../api'
import { useAuth } from '../auth'

const pageSize = 12
const filters = [
  ['all', 'All offers'],
  ['cdi', 'Full-time'],
  ['stage', 'Internship'],
  ['alternance', 'Work-study'],
  ['remote', 'Remote'],
]

export default function Annonces() {
  const { user, loading: sessionLoading } = useAuth()
  const [ads, setAds] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [retry, setRetry] = useState(0)
  const [query, setQuery] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    if (sessionLoading) return
    const controller = new AbortController()
    api(`/advertisements/?offset=${page * pageSize}&limit=${pageSize}`, { signal: controller.signal })
      .then(setAds)
      .catch((err) => { if (err.name !== 'AbortError') setError(err.message) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [page, retry, user?.id, sessionLoading])

  const visibleAds = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    return ads.filter((ad) => {
      const searchable = [ad.title, ad.short_description, ad.location, ad.contract_type, ad.company?.name]
        .filter(Boolean).join(' ').toLowerCase()
      const matchesQuery = !normalized || searchable.includes(normalized)
      const matchesFilter = filter === 'all'
        || ad.contract_type === filter
        || (filter === 'remote' && searchable.includes('remote'))
      return matchesQuery && matchesFilter
    })
  }, [ads, query, filter])

  function changePage(next) {
    setLoading(true)
    setError('')
    setPage(next)
  }

  return <section>
    <div className="hero">
      <p className="eyebrow">Your cosy corner for job hunting</p>
      <h1>Find a job that feels like home.</h1>
      <p>Internships, work-study and jobs gathered in one warm place. No duplicates, no endless tabs.</p>
    </div>

    <div className="board-toolbar">
      <label className="search-field">Search
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Job title, city, company…" />
      </label>
      <div>
        <div className="filter-row" role="list" aria-label="Filtres des offres">
          {filters.map(([key, label]) => <button
            className="secondary"
            key={key}
            type="button"
            aria-pressed={filter === key}
            onClick={() => setFilter(key)}
          >{label}</button>)}
        </div>
        <p className="offer-count">{visibleAds.length} offer{visibleAds.length > 1 ? 's' : ''}</p>
      </div>
    </div>

    {loading || sessionLoading ? <p role="status">Chargement des annonces…</p> : error ? <div role="alert">
      <p>{error}</p><button onClick={() => { setError(''); setLoading(true); setRetry(retry + 1) }}>Réessayer</button>
    </div> : <>
      {!visibleAds.length && <p>Aucune annonce ne correspond à votre recherche.</p>}
      <div className="annonces-list">{visibleAds.map((ad) => <Advertisement key={ad.id} ad={ad} />)}</div>
    </>}

    <nav className="pagination" aria-label="Pagination des annonces">
      <button className="secondary" disabled={loading || page === 0} onClick={() => changePage(page - 1)}>Précédent</button>
      <span>Page {page + 1}</span>
      <button className="secondary" disabled={loading || !!error || ads.length < pageSize} onClick={() => changePage(page + 1)}>Suivant</button>
    </nav>
  </section>
}
