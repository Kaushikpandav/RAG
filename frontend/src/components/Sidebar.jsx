import React, { useState } from 'react';
import { Database, X } from 'lucide-react';
import axios from 'axios';

const Sidebar = ({ mobileOpen, setMobileOpen }) => {
    const [ingesting, setIngesting] = useState(false);
    const [status, setStatus] = useState('');

    const triggerIngestion = async () => {
        try {
            setIngesting(true);
            setStatus('Starting ingestion...');
            await axios.post('/api/v1/ingestion/trigger');
            setStatus('Ingestion started in background.');
        } catch (error) {
            console.error(error);
            setStatus('Error triggering ingestion.');
        } finally {
            setTimeout(() => {
                setIngesting(false);
                setStatus('');
            }, 3000);
        }
    };

    return (
        <>
            {/* Overlay for mobile */}
            {mobileOpen && (
                <div
                    onClick={() => setMobileOpen(false)}
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0,0,0,0.5)',
                        zIndex: 10,
                        backdropFilter: 'blur(2px)'
                    }}
                />
            )}

            <aside className={`sidebar ${mobileOpen ? 'open' : ''}`} style={{
                width: '260px',
                backgroundColor: 'var(--color-bg-secondary)',
                borderRight: '1px solid var(--color-border)',
                display: 'flex',
                flexDirection: 'column',
                padding: '1rem',
                height: '100%',
                boxSizing: 'border-box',
                transition: 'transform 0.3s ease',
                zIndex: 20
                // Mobile styles are handled in index.css or via class
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                    {/* Traffic Lights - Hide on mobile if preferred, or keep */}
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#FF5F56' }}></div>
                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#FFBD2E' }}></div>
                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#27C93F' }}></div>
                    </div>

                    {/* Close button for mobile */}
                    <button
                        className="mobile-only"
                        onClick={() => setMobileOpen(false)}
                        style={{ background: 'none', border: 'none', color: 'var(--color-text-secondary)', cursor: 'pointer' }}
                    >
                        <X size={20} />
                    </button>
                </div>

                <div style={{ marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{
                        width: '40px',
                        height: '40px',
                        background: 'var(--color-bg-primary)',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        overflow: 'hidden',
                        border: '1px solid var(--color-border)'
                    }}>
                        <img src="/src/assets/rag_bot_icon.png" alt="Icon" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    </div>
                    <h1 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>RAG Bot</h1>
                </div>

                <div style={{ flex: 1 }}>
                    <h3 style={{
                        fontSize: '0.85rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                        color: 'var(--color-text-secondary)',
                        marginBottom: '1rem'
                    }}>
                        Knowledge Base
                    </h3>
                    <button
                        onClick={triggerIngestion}
                        disabled={ingesting}
                        style={{
                            width: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem',
                            borderRadius: 'var(--radius-md)',
                            backgroundColor: 'var(--color-bg-primary)',
                            border: '1px solid var(--color-border)',
                            color: 'var(--color-text-primary)',
                            cursor: ingesting ? 'wait' : 'pointer',
                            textAlign: 'left'
                        }}
                    >
                        <Database size={16} />
                        {ingesting ? 'Ingesting...' : 'Update Knowledge Base'}
                    </button>
                    {status && <p style={{ fontSize: '0.8rem', color: 'var(--color-accent)', marginTop: '0.5rem' }}>{status}</p>}
                </div>

                <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
                    <p style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>Powered by kaushikPandav</p>
                </div>
            </aside>
        </>
    );
};

export default Sidebar;
