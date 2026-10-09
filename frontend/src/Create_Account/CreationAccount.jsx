import { useState } from "react"
import style from './CreateAccount.module.css'
import { Link } from 'react-router-dom'

function CreateAccount() {

    const [email, setMail] = useState("")
    const [password, setPassword] = useState("")


    return (
        <>
            <div className={style.div}>
                <p className={style.login_title}>Création de compte</p>
                <form className={style.form}>
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
                    <button type="submit">Créer mon compte</button>
                </form>
                <div className={style.div_link}>
                    <Link to="/Login" className={style.link}>Se connecter</Link>
                </div>

            </div>
        </>
    )
}
export default CreateAccount