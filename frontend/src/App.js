import React, { useState } from 'react';
import './App.css';

function App() {
  // URL input related
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // Text input related
  const [textContent, setTextContent] = useState('');
  const [textLoading, setTextLoading] = useState(false);
  const [textMessage, setTextMessage] = useState('');

  // Chat related
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: 'Hello! I\'m your AI assistant. How can I help you today?' }
  ]);



  // Handle URL input
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('Processing...');
    try {
      const response = await fetch('http://localhost:8000/scrape-website', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      setMessage(data.message || 'Website content successfully scraped!');
    } catch (error) {
      setMessage('Processing failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle text input
  const handleTextSubmit = async (e) => {
    e.preventDefault();
    if (!textContent.trim()) return;
    
    setTextLoading(true);
    setTextMessage('Processing text...');
    try {
      const response = await fetch('http://localhost:8000/add-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: textContent }),
      });
      const data = await response.json();
      setTextMessage(data.message || 'Text content successfully added!');
      setTextContent(''); // Clear the text area after successful submission
    } catch (error) {
      setTextMessage('Processing failed: ' + error.message);
    } finally {
      setTextLoading(false);
    }
  };

  // Handle AI chat
  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const newHistory = [...chatHistory, { role: 'user', content: chatInput }];
    setChatHistory(newHistory);
    setChatLoading(true);
    setChatInput('');
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newHistory }),
      });
      const data = await response.json();
      setChatHistory([...newHistory, { role: 'assistant', content: data.answer || 'No AI response' }]);
    } catch (error) {
      setChatHistory([...newHistory, { role: 'assistant', content: 'Request failed: ' + error.message }]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Beauty Salon Q&A System</h1>
        <p className="subtitle">AI-powered website analysis and intelligent Q&A</p>
      </header>

              <main className="App-main">
        {/* Main Content */}
        <div className="main-content">
          {/* URL Input Module */}
          <div className="url-input-container">
            <h2>Enter Beauty Salon Website URL</h2>
            <form onSubmit={handleSubmit} className="url-form">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter beauty salon website URL (e.g., https://example.com)"
                required
                className="url-input"
              />
              <button type="submit" disabled={loading} className="submit-button">
                {loading ? 'Processing...' : 'Start Analysis'}
              </button>
            </form>
            {message && (
              <div className={`message ${loading ? 'loading' : ''}`}>{message}</div>
            )}
          </div>

          {/* Text Input Module */}
          <div className="text-input-container">
            <h2>Add Text Content</h2>
            <form onSubmit={handleTextSubmit} className="text-form">
              <textarea
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                placeholder="Enter salon information, services, prices, or any relevant content..."
                className="text-input"
                rows="6"
              />
              <button type="submit" disabled={textLoading || !textContent.trim()} className="submit-button">
                {textLoading ? 'Adding...' : 'Add to Database'}
              </button>
            </form>
            {textMessage && (
              <div className={`message ${textLoading ? 'loading' : ''}`}>{textMessage}</div>
            )}
          </div>

          {/* AI Chat Module */}
          <div className="chat-container">
            <h2>AI Chat</h2>
            <div className="chat-history">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`chat-msg ${msg.role}`}>
                  {msg.role === 'user' ? 'You: ' : 'AI: '}{msg.content}
                </div>
              ))}
              {chatLoading && <div className="chat-msg assistant">AI is typing...</div>}
            </div>
            <form onSubmit={handleChatSubmit} className="chat-form">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Enter your question..."
                className="chat-input"
                disabled={chatLoading}
              />
              <button type="submit" className="submit-button" disabled={chatLoading || !chatInput.trim()}>
                Send
              </button>
            </form>
          </div>
        </div>

        {/* Simple Instructions Sidebar */}
        <div className="instructions-sidebar">
          <h3>📖 How to Use</h3>
          <div className="step">
            <span className="step-num">1</span>
            <span>Enter website URL or add text content</span>
          </div>
          <div className="step">
            <span className="step-num">2</span>
            <span>Wait for processing</span>
          </div>
          <div className="step">
            <span className="step-num">3</span>
            <span>Ask questions about the salon</span>
          </div>
          
          <div className="text-input-info">
            <h4>✍️ Text Input:</h4>
            <p>Directly add salon information like services, prices, hours, or policies to the database.</p>
          </div>
          
          <div className="example-questions">
            <h4>💬 Try asking:</h4>
            <ul>
              <li>"What services are offered?"</li>
              <li>"What are the hours?"</li>
              <li>"How much do haircuts cost?"</li>
              <li>"Where is the salon located?"</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App; 