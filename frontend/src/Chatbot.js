import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { marked } from 'marked';

const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([{ text: "Hi! I'm your TrendThread Assistant. How can I help you?", sender: "bot" }]);
    const [input, setInput] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    // Auto-scroll to bottom of chat
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => { scrollToBottom(); }, [messages, isTyping]);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMsg = { text: input, sender: "user" };
        setMessages(prev => [...prev, userMsg]);
        setInput("");
        setIsTyping(true); // Start thinking animation

        try {
            // Updated to 127.0.0.1 for new system compatibility
            const res = await axios.post('http://127.0.0.1:5000/api/chat', { message: input });
            setMessages(prev => [...prev, { text: res.data.reply, sender: "bot" }]);
        } catch (err) {
            setMessages(prev => [...prev, { text: "Connection error. Please check if Flask is running.", sender: "bot" }]);
        } finally {
            setIsTyping(false); // Stop thinking animation
        }
    };

    return (
        <div className="chatbot-container">
            {isOpen && (
                <div className="chat-window">
                    <div className="chat-header">TrendThread Assistant</div>
                    <div className="chat-body">
                        {messages.map((m, i) => (
                            <div key={i} className={`chat-msg ${m.sender}`}>
                                {/* Use dangerouslySetInnerHTML so bolding and lists work */}
                                <div dangerouslySetInnerHTML={{ __html: marked.parse(m.text) }} />
                            </div>
                        ))}
                        {isTyping && (
                            <div className="chat-msg bot">
                                <div className="typing"><div className="dot"></div><div className="dot"></div><div className="dot"></div></div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                    <div className="chat-footer">
                        <input value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && sendMessage()} placeholder="Ask about our products..." />
                        <button onClick={sendMessage}>Send</button>
                    </div>
                </div>
            )}
            <button className="chat-toggle" onClick={() => setIsOpen(!isOpen)}>💬</button>
        </div>
    );
};

export default Chatbot;