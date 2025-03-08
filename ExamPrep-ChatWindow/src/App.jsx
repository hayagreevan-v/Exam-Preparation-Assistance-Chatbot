import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import './App.css'
import { UploadPage } from './components/UploadPage';
import ChatWindow from './components/ChatWindow';
import ImportExport from './components/ImportExport';

function App() {
    const [messages,setMessages] = useState([]);

    useEffect(()=>{
      axios.get("http://localhost:5000/chat").then((res)=> setMessages(res.data.chat));
    },[]);

    return(
      <div style={{display:'grid', justifyContent:"center", height:"100vh", gridTemplate:"1fr 1fr / 3fr 1fr"}}>
        <div style={{gridRow:"span 2"}}>
          <ChatWindow messages={messages} setMessages={setMessages} />
        </div>
        <div>
          <UploadPage />
        </div>
        <div>
          <ImportExport messages={messages} setMessages={setMessages}/>
        </div>
      </div>

    )
}

export default App
