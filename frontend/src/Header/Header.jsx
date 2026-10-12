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
    try {
      await logout()
      navigate('/Annonces')
    } catch (err) {
      setError(err.message)
    }
  }

  return <header className={style.header}>
    <Link to="/" className={style.brand} aria-label="tanière, retour aux offres">
      <span className={style.logoMark}>t</span>
      tanière
    </Link>
    <nav className={style.nav} aria-label="Navigation principale">
      <Link to="/Annonces" className={style.link}>Jobs</Link>
      <Link to="/Annonces" className={style.link}>Companies</Link>
      {user ? <>
        <Link to="/Account" className={style.link}>Mon compte</Link>
        {user.role === 'admin' && <Link to="/Admin" className={style.link}>Admin</Link>}
        <button className={style.ghostButton} onClick={disconnect}>Sign out</button>
      </> : <>
        <Link to="/Login" className={style.link}>Sign in</Link>
        <Link to="/CreateAccount" className={style.cta}>Create account</Link>
      </>}
    </nav>
    {error && <p className={style.error} role="alert">{error}</p>}
  </header>
}
