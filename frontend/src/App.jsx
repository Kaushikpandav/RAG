import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import axios from 'axios';
import { Menu } from 'lucide-react';

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your RAG assistant. Ask me anything about NVIDIA or OpenAI technologies.' }
  ]);
  const [loading, setLoading] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text) => {
    const newMessages = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const response = await axios.post('/api/v1/chat/message', {
        message: text,
        history: [] // Send history if needed
      });

      const botMessage = {
        role: 'assistant',
        content: response.data.response,
        context: response.data.context
      };

      setMessages([...newMessages, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages([...newMessages, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-window">
      <Sidebar mobileOpen={mobileOpen} setMobileOpen={setMobileOpen} />

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
        {/* Header Bar */}
        <div style={{
          height: '40px',
          background: 'var(--color-bg-primary)',
          borderBottom: '1px solid var(--color-border)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 1rem',
          justifyContent: 'space-between'
        }}>
          {/* Mobile Menu Button */}
          <button
            className="mobile-only"
            onClick={() => setMobileOpen(true)}
            style={{ background: 'none', border: 'none', color: 'var(--color-text-secondary)', cursor: 'pointer', padding: 0 }}
          >
            <Menu size={20} />
          </button>

          {/* Spacer to keep title centered if we had one, or just ease of layout */}
          <div></div>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', padding: '2rem' }}>
          <div className="container">
            {messages.map((msg, idx) => (
              <ChatMessage key={idx} message={msg} />
            ))}
            {loading && (
              <div style={{ padding: '0 1rem', display: 'flex', gap: '0.75rem' }}>
                <div style={{ width: '2.5rem' }}></div>
                <div style={{ color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>Thinking...</div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
        <ChatInput onSend={handleSendMessage} disabled={loading} />
      </main>
    </div>
  );
}

export default App;
