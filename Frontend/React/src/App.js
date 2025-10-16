import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import './index.css';

const API_START = "https://hculxoeutg.execute-api.us-east-1.amazonaws.com/dev/Hackathon-sales";
const API_RESULT = "https://hculxoeutg.execute-api.us-east-1.amazonaws.com/dev/Hackathon-sales-result";

function App() {
  const [sessionId, setSessionId] = useState(uuidv4());
  const [chat, setChat] = useState([]);
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const chatContainerRef = useRef(null);

  // Auto-scroll to bottom when chat updates
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chat, isLoading]);

  const handleNewSession = () => {
    setSessionId(uuidv4());
    setChat([]);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  };

  const pollForResult = async (jobId) => {
    const maxAttempts = 60; // 2 minutes with 2-second intervals
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      
      try {
        const response = await axios.get(API_RESULT, {
          params: { job_id: jobId }
        });
        
        if (response.data.status === "completed") {
          return response.data.response;
        }
      } catch (error) {
        console.error('Error polling for result:', error);
      }
    }
    
    throw new Error('Response not ready, try again later.');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;

    const userMessage = { role: 'user', content: question };
    setChat(prev => [...prev, userMessage]);
    setQuestion('');
    setIsLoading(true);

    try {
      // Start the job
      const startResponse = await axios.post(API_START, {
        question: question,
        session_id: sessionId
      });
      
      const jobId = startResponse.data.job_id;
      
      // Poll for result
      const result = await pollForResult(jobId);
      
      const assistantMessage = { role: 'assistant', content: result };
      setChat(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { 
        role: 'assistant', 
        content: error.message || 'An error occurred. Please try again.' 
      };
      setChat(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>⚙️ Controls</h2>
        <button className="new-session-btn" onClick={handleNewSession}>
          🆕 New Session
        </button>
        {showSuccess && (
          <div className="success-message">
            ✅ New session started
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <div className="chat-header">
          <h1>🤖 Sales Assistant ChatBot</h1>
        </div>

        {/* Chat Messages */}
        <div className="chat-container" ref={chatContainerRef}>
          {chat.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-bubble">
                {msg.role === 'assistant' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-bubble">
                <div className="loading">
                  <div className="spinner"></div>
                  🤔 Thinking...
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="chat-input-container">
          <form className="chat-input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="chat-input"
              placeholder="Ask something..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={isLoading}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={isLoading || !question.trim()}
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;