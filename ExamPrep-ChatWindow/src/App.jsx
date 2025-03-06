import { useState, useRef } from 'react'
import axios from 'axios'
import './App.css'
import { UploadPage } from './components/UploadPage';
import ChatWindow from './components/ChatWindow';

function App() {
    

    return(
      <div style={{display:'flex', justifyContent:"center",gap:0}}>
        <div>
          <ChatWindow />
        </div>
        <div>
          <UploadPage />
        </div>

      </div>

    )
}

export default App
