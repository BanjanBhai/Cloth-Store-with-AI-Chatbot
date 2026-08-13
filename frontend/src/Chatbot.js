import React, { useState } from 'react';
import axios from 'axios';
import { marked } from 'marked';

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([{ text: "Hi! How can I help you today?", sender: "bot" }]);
    const [input, setInput] = useState("");

    const sendMessage = async () => {
        if (!input.trim()) return;
        const newMessages = [...messages, { text: input, sender: "user" }];
        setMessages(newMessages);
        setInput("");

        try {
            const res = await axios.post('http://localhost:5000/api/chat', { message: input });
            setMessages([...newMessages, { text: res.data.reply, sender: "bot" }]);
        } catch (err) {
            setMessages([...newMessages, { text: "Error connecting to AI.", sender: "bot" }]);
        }
    };

    return (
        <div className="chatbot-container">
            {isOpen && (
                <div className="chat-window">
                    <div className="chat-header">TrendThread Assistant</div>
                    <div className="chat-body">
                        {messages.map((m, i) => (
                            <div key={i} className={`chat-msg ${m.sender}`}>{m.text}</div>
                        ))}
                    </div>
                    <div className="chat-footer">
                        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendMessage()} placeholder="Ask anything..." />
                        <button onClick={sendMessage}>Send</button>
                    </div>
                </div>
            )}
            <button className="chat-toggle" onClick={() => setIsOpen(!isOpen)}>💬</button>
        </div>
    );
};

export default Chatbot;