import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Bot } from 'lucide-react';

const ChatMessage = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div className={`message-row ${isUser ? 'user-row' : 'bot-row'}`} style={{
            display: 'flex',
            justifyContent: isUser ? 'flex-end' : 'flex-start',
            marginBottom: '1rem',
            padding: '0 1rem'
        }}>
            <div className="message-container" style={{
                display: 'flex',
                flexDirection: isUser ? 'row-reverse' : 'row',
                maxWidth: '80%',
                gap: '0.75rem'
            }}>
                <div className="avatar" style={{
                    width: '2.5rem',
                    height: '2.5rem',
                    borderRadius: '50%',
                    backgroundColor: isUser ? 'var(--color-accent)' : 'var(--color-bg-secondary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0
                }}>
                    {isUser ? <User size={20} color="white" /> : <Bot size={20} color="var(--color-accent)" />}
                </div>

                <div className="bubble" style={{
                    backgroundColor: isUser ? 'var(--color-accent)' : 'var(--color-bg-secondary)',
                    color: isUser ? '#fff' : 'var(--color-text-primary)',
                    padding: '0.75rem 1rem',
                    borderRadius: '1rem',
                    borderTopLeftRadius: isUser ? '1rem' : '0',
                    borderTopRightRadius: isUser ? '0' : '1rem',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }}>
                    <div className="markdown-content">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>
                    {message.context && (
                        <div className="context-expander" style={{ marginTop: '0.5rem', fontSize: '0.8rem', opacity: 0.8 }}>
                            <details>
                                <summary style={{ cursor: 'pointer' }}>View Sources</summary>
                                <pre style={{
                                    marginTop: '0.5rem',
                                    backgroundColor: 'rgba(0,0,0,0.2)',
                                    padding: '0.5rem',
                                    borderRadius: '0.25rem',
                                    whiteSpace: 'pre-wrap',
                                    overflowX: 'auto'
                                }}>
                                    {message.context}
                                </pre>
                            </details>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ChatMessage;
