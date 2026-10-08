import { Link } from 'react-router-dom'
function Header () {
    return (
        <>
            <div>
                <div>
                    <img src="" alt="" />
                </div>
                <nav>
                    <ul>
                        <Link to="/">Accueil</Link>
                        <Link to="/Annonces">Annonces</Link>
                        <Link to="/Login">Login</Link>
                    </ul>
                </nav>
            </div>
        </>
    )
}

export default Header