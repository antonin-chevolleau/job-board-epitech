import { useState, useEffect } from 'react'
import Advertisement from '../Advertisement/Advertisement.jsx'
import { api } from '../api'
import { useAuth } from '../auth'

const pageSize = 12
export default function Annonces() {
  const { user, loading: sessionLoading } = useAuth()
  const [ads, setAds] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(0)
  const [retry, setRetry] = useState(0)

  useEffect(() => {
    if (sessionLoading) return
    const controller = new AbortController()
    api(`/advertisements/?offset=${page * pageSize}&limit=${pageSize}`, { signal: controller.signal })
      .then(setAds)
      .catch((err) => { if (err.name !== 'AbortError') setError(err.message) })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [page, retry, user?.id, sessionLoading])

  function changePage(next) { setLoading(true); setError(''); setPage(next) }
  return <section>
    <div className="hero"><p>Votre prochain chapitre commence ici</p><h1>Trouvez le poste qui vous correspond</h1><p>Découvrez les offres et échangez avec les recruteurs.</p></div>
    {loading || sessionLoading ? <p role="status">Chargement des annonces…</p> : error ? <div role="alert">
      <p>{error}</p><button onClick={() => { setError(''); setLoading(true); setRetry(retry + 1) }}>Réessayer</button>
    </div> : <>
      {!ads.length && <p>Aucune annonce disponible sur cette page.</p>}
      <div className="annonces-list">{ads.map((ad) => <Advertisement key={ad.id} ad={ad} />)}</div>
    </>}
    <nav className="pagination" aria-label="Pagination des annonces">
      <button disabled={loading || page === 0} onClick={() => changePage(page - 1)}>Précédent</button>
      <span>Page {page + 1}</span>
      <button disabled={loading || !!error || ads.length < pageSize} onClick={() => changePage(page + 1)}>Suivant</button>
    </nav>
  </section>
}
