import { useState } from 'react'
import {Routes, Route} from 'react-router-dom'
import './App.css'
import Header from './Header/Header.jsx'
import Login from './Login/Login.jsx'
import CreateAccount from './Create_Account/CreationAccount.jsx'
import Annonces from './Annonces/Annonces.jsx'


function App() {


  return (
    <>
      <Header></Header>
      <Routes>
        <Route>
          <Route path="/CreateAccount" element={<CreateAccount />} />
          <Route path="/Login" element={<Login />} />
          <Route path="/Annonces" element={<Annonces />} />
        </Route>
      </Routes>
    </>
  )
}

export default App
