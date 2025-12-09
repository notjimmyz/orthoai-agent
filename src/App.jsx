import { useState, useRef, useEffect } from 'react'
import './App.css'

function AgentPanel({ agentName, agentColor, agentUrl, defaultPort }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [url, setUrl] = useState(agentUrl || `http://localhost:${defaultPort}`)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const checkConnection = async () => {
    try {
      const response = await fetch(`/api/check-agent?url=${encodeURIComponent(url)}`)
      const data = await response.json()
      setIsConnected(data.ready || false)
    } catch (error) {
      setIsConnected(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user', content: input, timestamp: new Date() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, message: input })
      })

      const data = await response.json()
      
      if (data.error) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `Error: ${data.error}`,
          timestamp: new Date()
        }])
      } else {
        const assistantMessage = {
          role: 'assistant',
          content: data.response || 'No response received',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, assistantMessage])
      }
    } catch (error) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Error: ${error.message}`,
        timestamp: new Date()
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearMessages = () => {
    setMessages([])
  }

  return (
    <div className="agent-panel">
      <div className="agent-header">
        <div className="agent-title">
          <div className="agent-indicator" style={{ backgroundColor: agentColor }}></div>
          <h2>{agentName}</h2>
          <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
            <span className="status-dot"></span>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
        <div className="agent-controls">
          <input
            type="text"
            className="url-input"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Agent URL"
          />
          <button onClick={checkConnection} className="btn-check">Check</button>
          <button onClick={clearMessages} className="btn-clear">Clear</button>
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>No messages yet. Start a conversation with {agentName}.</p>
          </div>
        ) : (
          messages.map((msg, idx) => {
            const rgbColor = agentColor === '#10b981' 
              ? '16, 185, 129' 
              : '59, 130, 246';
            return (
              <div key={idx} className={`message ${msg.role}`}>
                <div 
                  className="message-content"
                  style={msg.role === 'user' ? {
                    background: `rgba(${rgbColor}, 0.15)`,
                    borderColor: `rgba(${rgbColor}, 0.2)`
                  } : {}}
                >
                  <pre>{msg.content}</pre>
                </div>
                <div className="message-time">
                  {msg.timestamp.toLocaleTimeString()}
                </div>
              </div>
            );
          })
        )}
        {isLoading && (
          <div className="message assistant">
            <div className="message-content">
              <div className="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={`Message ${agentName}...`}
          rows={3}
          disabled={isLoading}
        />
        <button
          onClick={sendMessage}
          disabled={!input.trim() || isLoading}
          className="btn-send"
          style={{ 
            background: `linear-gradient(135deg, ${agentColor}40, ${agentColor}20)`,
            borderColor: `${agentColor}50`
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Agent Interface</h1>
        <p>Interact with Green and White Agents</p>
      </header>

      <div className="agents-container">
        <AgentPanel
          agentName="Green Agent"
          agentColor="#10b981"
          defaultPort={9001}
        />
        <AgentPanel
          agentName="White Agent"
          agentColor="#3b82f6"
          defaultPort={9002}
        />
      </div>
    </div>
  )
}

export default App
