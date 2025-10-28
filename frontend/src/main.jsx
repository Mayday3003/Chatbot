import React from 'react'
import { createRoot } from 'react-dom/client'
import ChatWidget from './components/ChatWidget'

function App(){
  return <div><h1>Chatbot</h1><ChatWidget /></div>
}

createRoot(document.getElementById('root')).render(<App />)
