import { useState, useEffect, useRef } from 'react'
import { C, css } from '../styles'

export default function ChatPanel({ messages, onSend, disabled, phase, activeField }) {
  const [input, setInput]   = useState('')
  const threadRef           = useRef(null)

  useEffect(() => {
    if (threadRef.current) threadRef.current.scrollTop = threadRef.current.scrollHeight
  }, [messages])

  function handleSend() {
    if (!input.trim() || disabled) return
    onSend(input.trim())
    setInput('')
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: C.bgBase }}>

      {/* Header */}
      <div style={{ padding: '20px 24px 16px', background: C.navy, borderBottom: `1px solid ${C.border}`, flexShrink: 0 }}>
        <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: C.orange, margin: '0 0 4px' }}>AI Advisor</p>
        <h2 style={{ fontSize: 20, fontWeight: 700, color: '#fff', margin: 0 }}>Follow-up questions</h2>
      </div>

      {/* Thread */}
      <div ref={threadRef} style={{ flex: 1, overflowY: 'auto', padding: 16, display: 'flex', flexDirection: 'column' }}>
        {messages.length === 0 && phase === 'centre' ? (
          <WelcomeScreen />
        ) : messages.length === 0 ? (
          <p style={{ fontSize: 13, color: C.textFaint, textAlign: 'center', marginTop: 40 }}>
            Click "Ask follow-up ↗" on any field to start a conversation.
          </p>
        ) : (
          messages.map(msg => (
            <div key={msg.id} style={{ marginBottom: 12 }}>
              <p style={css.roleLabel(msg.role)}>
                {msg.role === 'user' ? 'You' : 'AI advisor'}
                {msg.fieldId && <span style={{ fontWeight: 400 }}> · {msg.fieldId}</span>}
              </p>
              <div style={css.bubble(msg.role)}>{msg.content}</div>
            </div>
          ))
        )}
      </div>

      {/* Input */}
      <div style={{ padding: 12, borderTop: `1px solid ${C.border}`, flexShrink: 0, display: 'flex', gap: 8 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          disabled={disabled}
          placeholder={disabled ? 'Submit your profile first...' : activeField ? `Ask about ${activeField.fieldId}...` : 'Ask a follow-up question...'}
          style={{ flex: 1, padding: '9px 14px', fontSize: 13, border: `1px solid ${C.border}`, borderRadius: 4, fontFamily: 'inherit', color: C.textPrimary, background: disabled ? C.bgPanel : '#fff', opacity: disabled ? 0.6 : 1, cursor: disabled ? 'not-allowed' : 'text', outline: 'none' }} />
        <button onClick={handleSend} disabled={disabled || !input.trim()}
          style={{ padding: '9px 16px', background: (disabled || !input.trim()) ? C.borderLight : C.orange, color: '#fff', border: 'none', borderRadius: 4, fontSize: 12, fontWeight: 600, cursor: (disabled || !input.trim()) ? 'not-allowed' : 'pointer', fontFamily: 'inherit', transition: 'background 0.15s', flexShrink: 0 }}>
          Send
        </button>
      </div>
    </div>
  )
}

function WelcomeScreen() {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', paddingBottom: 40 }}>
      <style>{`
        @keyframes ripple { 0% { transform: scale(0.5); opacity: 0.4; } 100% { transform: scale(1.6); opacity: 0; } }
        @keyframes floatIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes gentleFloat { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
      `}</style>

      {/* Animated shield */}
      <div style={{ position: 'relative', width: 140, height: 140, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 28, animation: 'floatIn 0.7s cubic-bezier(0.22,1,0.36,1) both' }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{ position: 'absolute', width: 140, height: 140, borderRadius: '50%', border: `1.5px solid ${C.orange}`, opacity: 0, animation: `ripple 3s ease-out ${i}s infinite` }} />
        ))}
        <div style={{ position: 'absolute', width: 90, height: 90, borderRadius: '50%', background: `radial-gradient(circle, rgba(255,153,0,0.08) 0%, transparent 70%)` }} />
        <div style={{ width: 64, height: 64, background: C.navy, borderRadius: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', animation: 'gentleFloat 4s ease-in-out infinite', boxShadow: '0 4px 20px rgba(35,47,62,0.15)', position: 'relative', zIndex: 1 }}>
          <svg width="32" height="32" fill="none" stroke={C.orange} strokeWidth="1.8" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
          </svg>
        </div>
      </div>

      {/* Text */}
      <div style={{ textAlign: 'center', animation: 'floatIn 0.7s 0.1s cubic-bezier(0.22,1,0.36,1) both' }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: C.textPrimary, margin: '0 0 8px' }}>Welcome, there</h2>
        <p style={{ fontSize: 13, color: C.textMuted, lineHeight: 1.7, maxWidth: 340 }}>
          I'll analyse your company profile and generate tailored AWS security configurations — with real compliance citations for every recommendation.
        </p>
      </div>
    </div>
  )
}
