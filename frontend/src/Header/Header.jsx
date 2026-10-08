import { Link } from 'react-router-dom'
import style  from './Header.module.css'
function Header () {
    return (
        <>
            <div className={style.div_header}>
                <div>
                    <img src="public/images/home_icon.png" alt="icon_home" className={style.image_icon}/>
                </div>
                <nav>
                    <ul>
                        <Link to="/" className={style.link}>Accueil</Link>
                        <Link to="/Annonces" className={style.link}>Annonces</Link>
                        <Link to="/Login" className={style.link}>Login</Link>
                    </ul>
                </nav>
            </div>
        </>
    );
}

export default Header