import { useState } from 'react'
import axios from 'axios'
import './App.css'

function App() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
  
    // Function to handle message sending
    const sendMessage = async () => {
      if (!input) return;
  
      // Add user's message to chat window
      const userMessage = { sender: "user", text: input };
      setMessages([...messages, userMessage]);
  
      try {
        // Call your backend API here (replace `/api/chat` with your endpoint)
        const response = await axios.post(
            "http://localhost:5000/chat",
            { query: input },  // Sending JSON data
            { headers: { "Content-Type": "application/json" } }  // Specify JSON format
          );
        console.log(input)
        const botMessage = { sender: "bot", text: response.data.output };
  
        // Update messages with bot response
        setMessages((prevMessages) => [...prevMessages, botMessage]);
      } catch (error) {
        console.error("Error sending message:", error);
      }
  
      setInput("");
    };

    return(
        <div className="chat-window">
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender === "user" ? "user" : "bot"}`}
          >
            {(msg.text).split('\n').map((i, ind) => (
              <div>
                <p>{i}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="chat-input">
        <input
          type="text"
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
    )
}

export default App
