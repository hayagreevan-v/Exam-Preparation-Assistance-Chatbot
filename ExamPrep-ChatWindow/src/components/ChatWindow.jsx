import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import '../App.css'

const ChatWindow = ({messages, setMessages}) =>{
    // const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [disabled, setDisabled] = useState(false);
  
    const clearChat = async () =>{
      const res = await axios.get("http://localhost:5000/clear-chat");
      setMessages(res.data.chat);
    }
    // Function to handle message sending
    const sendMessage = async () => {
      if (!input) return;
  
      // Add user's message to chat window
      const userMessage = { sender: "user", text: input };
      setMessages([...messages, userMessage]);
  
      try {
        setInput("Loading...");
        setDisabled(true);
        const response = await axios.post(
            "http://localhost:5000/chat",
            { query: input },  // Sending JSON data
            { headers: { "Content-Type": "application/json" } }  // Specify JSON format
          );
        console.log(input)
        // const botMessage = { sender: "bot", text: response.data.output };
  
        // Update messages with bot response
        setMessages(response.data.chat);
      } catch (error) {
        console.error("Error sending message:", error);
      }
      setDisabled(false);
      setInput("");
    };

    // useEffect(()=>{
    //     axios.get("http://localhost:5000/chat").then((res)=> setMessages(res.data.chat));
    // },[])

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
              disabled={disabled}
            />
            <button onClick={sendMessage} disabled={disabled}>Send</button>
            <button onClick={clearChat}>Clear chat</button>
          </div>
        </div>
    )
}

export default ChatWindow;
