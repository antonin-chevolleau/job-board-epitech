import { useEffect, useState } from 'react'
import Advertisement from '../Advertisement/Advertisement.jsx'
import { api } from '../api'
import { useAuth } from '../auth'

const pageSize = 12
const contractTypes = ['CDI', 'CDD', 'Stage', 'Alternance', 'Freelance']

export default function Annonces() {
  const { user, loading: sessionLoading } = useAuth()
  const [ads, setAds] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [retry, setRetry] = useState(0)
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('')
  const [contract, setContract] = useState('')
  // text typed by the user, applied to the search after a short pause
  const [search, setSearch] = useState({ q: '', location: '' })

  useEffect(() => {
    const timer = setTimeout(() => {
      const next = { q: query.trim(), location: location.trim() }
      if (next.q === search.q && next.location === search.location) return
      setSearch(next)
      setLoading(true)
      setError('')
      setPage(0)
    }, 300)
    return () => clearTimeout(timer)
  }, [query, location, search])

  useEffect(() => {
    if (sessionLoading) return
    const controller = new AbortController()
    const params = new URLSearchParams({ page: page + 1, limit: pageSize })
    if (search.q) params.set('q', search.q)
    if (search.location) params.set('location', search.location)
    if (contract) params.set('contract_type', contract)
    api(`/advertisements?${params}`, { signal: controller.signal })
      .then((data) => { setAds(data.items); setTotal(data.total) })
      .catch((err) => { if (err.name !== 'AbortError') setError(err.message) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [page, retry, search, contract, user?.id, sessionLoading])

  function refresh(change) {
    setLoading(true)
    setError('')
    change()
  }

  const pageCount = Math.max(1, Math.ceil(total / pageSize))

  return <section>
    <div className="hero">
      <p className="eyebrow">Votre coin douillet pour chercher un emploi</p>
      <h1>Trouvez un poste où vous vous sentez chez vous.</h1>
      <p>Stages, alternances et emplois réunis au même endroit. Sans doublons, sans onglets à n’en plus finir.</p>
    </div>

    <div className="board-toolbar">
      <label className="search-field">Recherche
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Intitulé du poste, mot-clé…" />
      </label>
      <label className="search-field">Lieu
        <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Ville…" />
      </label>
      <div>
        <div className="filter-row" role="list" aria-label="Filtres des offres">
          {['', ...contractTypes].map((type) => <button
            className="secondary"
            key={type}
            type="button"
            aria-pressed={contract === type}
            onClick={() => { if (contract !== type) refresh(() => { setContract(type); setPage(0) }) }}
          >{type || 'Toutes les offres'}</button>)}
        </div>
        <p className="offer-count">{total} offre{total > 1 ? 's' : ''}</p>
      </div>
    </div>

    {loading || sessionLoading ? <p role="status">Chargement des annonces…</p> : error ? <div role="alert">
      <p>{error}</p><button onClick={() => refresh(() => setRetry(retry + 1))}>Réessayer</button>
    </div> : <>
      {!ads.length && <p>Aucune annonce ne correspond à votre recherche.</p>}
      <div className="annonces-list">{ads.map((ad) => <Advertisement key={ad.id} ad={ad} />)}</div>
    </>}

    <nav className="pagination" aria-label="Pagination des annonces">
      <button className="secondary" disabled={loading || page === 0} onClick={() => refresh(() => setPage(page - 1))}>Précédent</button>
      <span>Page {page + 1} / {pageCount}</span>
      <button className="secondary" disabled={loading || !!error || page + 1 >= pageCount} onClick={() => refresh(() => setPage(page + 1))}>Suivant</button>
    </nav>
  </section>
}
