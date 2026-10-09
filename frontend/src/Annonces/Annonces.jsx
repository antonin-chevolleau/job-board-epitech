import { useState, useEffect } from 'react'
import Advertisement from '../Advertisement/Advertisement.jsx'

function Annonces () {
    const [ads, setAds] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetch('https://localhost/api/advertisement') // Remplace par l'URL de ton API
            .then((response) => {
                if (!response.ok) {
                    throw new Error('Erreur lors de la récupération des annonces')
                }
                return response.json()
            })
            .then((data) => {
                setAds(data)
                setLoading(false)
            })
            .catch((err) => {
                setError(err.message)
                setLoading(false)
            })
    }, []) // Le tableau vide [] exécute le fetch une seule fois au chargement

    if (loading) return <p>Chargement des annonces...</p>
    if (error) return <p>Erreur : {error}</p>

    return (
        <section className="annonces-list">
            {ads.map((ad) => (
                <Advertisement
                    key={ad.id} // Nécessaire pour React (utilise l'ID unique de ton API)
                    job_title={ad.job_title}
                    contract_type={ad.contract_type}
                    create_at={ad.create_at}
                    location={ad.location}
                    short_description={ad.short_description}
                />
            ))}
        </section>
    )
}

export default Annonces