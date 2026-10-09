import { useState } from 'react'
import {Routes, Route} from 'react-router-dom'
import './App.css'
import Header from './Header/Header.jsx'
import Login from './Login/Login.jsx'
import CreateAccount from './Create_Account/CreationAccount.jsx'


function App() {


  return (
    <>
      <Header></Header>
      <Routes>
        <Route>
          <Route path="/CreateAccount" element={<CreateAccount />} />
          <Route path="/Login" element={<Login />} />
        </Route>
      </Routes>
    </>
  )
}

export default App
