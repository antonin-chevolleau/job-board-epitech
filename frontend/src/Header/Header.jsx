import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import style from './Header.module.css'

export default function Header() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function disconnect() {
    logout()
    navigate('/Annonces')
  }

  return <header className={style.header}>
    <Link to="/" className={style.brand} aria-label="tanière, retour aux offres">
      <span className={style.logoMark}>t</span>
      tanière
    </Link>
    <nav className={style.nav} aria-label="Navigation principale">
      <Link to="/Annonces" className={style.link}>Offres</Link>
      {user ? <>
        <Link to="/Account" className={style.link}>Mon compte</Link>
        {user.role === 'admin' && <Link to="/Admin" className={style.link}>Admin</Link>}
        <button className={style.ghostButton} onClick={disconnect}>Se déconnecter</button>
      </> : <>
        <Link to="/Login" className={style.link}>Se connecter</Link>
        <Link to="/CreateAccount" className={style.cta}>Créer un compte</Link>
      </>}
    </nav>
  </header>
}
