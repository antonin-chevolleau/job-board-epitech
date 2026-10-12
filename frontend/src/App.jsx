import { Navigate, Routes, Route } from 'react-router-dom'
import './App.css'
import Header from './Header/Header.jsx'
import Login from './Login/Login.jsx'
import CreateAccount from './Create_Account/CreationAccount.jsx'
import Annonces from './Annonces/Annonces.jsx'
import Admin from './Admin/Admin.jsx'
import AuthProvider from './AuthProvider.jsx'
import { useAuth } from './auth'

function Protected({ children, admin = false }) {
  const { user, loading } = useAuth()
  if (loading) return <p role="status">Chargement de la session…</p>
  if (!user) return <Navigate to="/Login" replace />
  if (admin && user.role !== 'admin') return <Navigate to="/Annonces" replace />
  return children
}

export default function App() {
  return <AuthProvider>
    <Header />
    <main>
      <Routes>
        <Route path="/" element={<Navigate to="/Annonces" replace />} />
        <Route path="/CreateAccount" element={<CreateAccount />} />
        <Route path="/Login" element={<Login />} />
        <Route path="/Annonces" element={<Annonces />} />
        <Route path="/Account" element={<Protected><CreateAccount editing /></Protected>} />
        <Route path="/Admin" element={<Protected admin><Admin /></Protected>} />
        <Route path="*" element={<p>Cette page n’existe pas.</p>} />
      </Routes>
    </main>
  </AuthProvider>
}
