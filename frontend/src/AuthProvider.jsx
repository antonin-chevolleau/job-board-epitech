import { useEffect, useState } from 'react'
import { api, setToken } from './api'
import { AuthContext } from './auth'

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    const expire = () => setUser(null)
    window.addEventListener('session-expired', expire)
    api('/auth/me').then((person) => {
      if (active) setUser(person)
    }).catch(() => {
      if (active) setToken(null)
    }).finally(() => { if (active) setLoading(false) })
    return () => { active = false; window.removeEventListener('session-expired', expire) }
  }, [])

  async function login(credentials) {
    const result = await api('/auth/login', { method: 'POST', form: true, body: credentials })
    setToken(result.access_token)
    const person = await api('/auth/me')
    setUser(person)
    return person
  }

  function logout() {
    setToken(null)
    setUser(null)
  }

  return <AuthContext.Provider value={{ user, loading, login, logout, setUser }}>
    {children}
  </AuthContext.Provider>
}
