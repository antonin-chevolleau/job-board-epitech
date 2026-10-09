import { Link } from 'react-router-dom'
import style from './Login.module.css'
import { useState } from 'react'

function Login() {

    const [email, setMail] = useState("")
    const [password, setPassword] = useState("")


    const StartConnection = (event) => {
        event.preventDefault()
        console.log("création du compte avec : ", { email, password })
    }


    return (
        <>
            <div className={style.div}>
                <p className={style.login_title}>Login</p>
                <form className={style.form} onSubmit={StartConnection}>
                    <label htmlFor="email">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setMail(e.target.value)}
                        className={style.input}
                        required
                    />
                    <label htmlFor="password">Mot de passe</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className={style.input}
                        required
                    />
                    <button type="submit">Se connecter</button>
                </form>
                <div className={style.div_link}>
                    <Link to="/CreateAccount" className={style.link}>J'ai pas de compte</Link>
                </div>

            </div>
        </>
    )
}
export default Login