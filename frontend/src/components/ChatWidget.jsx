import React, { useState, useEffect } from 'react'

export default function ChatWidget(){
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [text, setText] = useState('')

  useEffect(()=>{
    // create session
    fetch('/api/chat/session/', {method: 'POST'}).then(r=>r.json()).then(d=>setSession(d.session_id))
  },[])

  const send = async ()=>{
    if(!text) return
    setMessages(prev=>[...prev, {sender:'user', text}])
    const resp = await fetch('/api/chat/message/', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({session_id: session, text})})
    const data = await resp.json()
    setMessages(prev=>[...prev, {sender:'bot', text: data.bot}])
    setText('')
  }

  return (
    <div style={{border:'1px solid #ddd', padding:10, width:400}}>
      <div style={{height:300, overflow:'auto', background:'#f9f9f9', padding:8}}>
        {messages.map((m,i)=>(<div key={i}><b>{m.sender}:</b> {m.text}</div>))}
      </div>
      <div style={{marginTop:8}}>
        <input value={text} onChange={e=>setText(e.target.value)} style={{width:'80%'}} />
        <button onClick={send}>Enviar</button>
      </div>
    </div>
  )
}
