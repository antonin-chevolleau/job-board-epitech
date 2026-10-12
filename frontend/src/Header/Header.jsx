import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import style from './Header.module.css'

export default function Header() {
  const { user, logout } = useAuth()
  const [error, setError] = useState('')
  const navigate = useNavigate()
  async function disconnect() {
    setError('')
    try { await logout(); navigate('/Annonces') }
    catch (err) { setError(err.message) }
  }
  return <header className={style.div_header}>
    <Link to="/" className="brand">JobBoard</Link>
    <nav aria-label="Navigation principale">
      <Link to="/Annonces" className={style.link}>Annonces</Link>
      {user ? <>
        <Link to="/Account" className={style.link}>Mon compte</Link>
        {user.role === 'admin' && <Link to="/Admin" className={style.link}>Administration</Link>}
        <button onClick={disconnect}>Déconnexion</button>
      </> : <Link to="/Login" className={style.link}>Connexion</Link>}
    </nav>
    {error && <p role="alert">{error}</p>}
  </header>
}
