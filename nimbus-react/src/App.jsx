import { useState, useRef, useCallback } from 'react'
import { extractIntent, fetchSchema, generateConfig, explainField } from './api'
import LeftPanel   from './components/LeftPanel'
import ChatPanel   from './components/ChatPanel'
import ConfigPanel from './components/ConfigPanel'
import { C } from './styles'

// Phase constants
const PHASE_WELCOME = 'welcome'
const PHASE_DONE    = 'done'

export default function App() {
  const [phase,        setPhase]        = useState(PHASE_WELCOME)
  const [session,      setSession]      = useState(null)
  const [schema,       setSchema]       = useState(null)
  const [config,       setConfig]       = useState(null)
  const [messages,     setMessages]     = useState([])   // shared conversation history
  const [activeField,  setActiveField]  = useState(null) // { fieldId, label, value, reason }
  const [chatDisabled, setChatDisabled] = useState(true)
  const [error,        setError]        = useState('')

  // Transition animation state
  const [chatSliding,   setChatSliding]   = useState(false)   // chat sliding left
  const [configVisible, setConfigVisible] = useState(false)   // config fading in
  const [rightVisible,  setRightVisible]  = useState(false)   // right panel expanding

  const appendMsg = useCallback((role, content, fieldId = null) => {
    setMessages(prev => [...prev, { role, content, fieldId, id: Date.now() + Math.random() }])
  }, [])

  // ── Main pipeline ──────────────────────────────────────────────────────────
  async function handleSubmit(description, service) {
    setError('')
    setChatDisabled(false)
    setMessages([])

    try {
      // Step 1 — intent
      appendMsg('ai', 'Analysing company profile...')
      const intentData = await extractIntent(description, service)
      setSession(intentData)

      // Step 2 — schema
      appendMsg('ai', `Fetching ${service} field names via AWS Docs MCP...`)
      const schemaData = await fetchSchema(service, intentData.sessionId)
      setSchema(schemaData.schema)

      // Step 3 — config
      appendMsg('ai', `Generating tailored recommendations for your ${intentData.intent?.industry || service} profile...`)
      const configData = await generateConfig(intentData.sessionId, schemaData.schema, service)
      setConfig(configData.config)

      // Trigger smooth transition after short pause
      setTimeout(() => doTransition(), 800)

    } catch (err) {
      appendMsg('ai', `⚠ ${err.message} — check the backend is running.`)
      setError(err.message)
    }
  }

  function doTransition() {
    // Step 1: slide chat left + fade out (400ms)
    setChatSliding(true)

    setTimeout(() => {
      // Step 2: show config (slide in from right) + expand right panel
      setPhase(PHASE_DONE)
      setConfigVisible(true)
      setRightVisible(true)
    }, 420)
  }

  // ── Follow-up / explain ────────────────────────────────────────────────────
  async function handleSend(message) {
    if (!message.trim() || !session) return
    const fId = activeField?.fieldId || null

    appendMsg('user', message, fId)
    try {
      const data = await explainField(
        session.sessionId,
        fId,
        activeField?.label || null,
        activeField?.value ?? null,
        activeField?.reason || null,
        message
      )
      appendMsg('ai', data.response, fId)

      // Live config update
      if (data.configUpdate) {
        const u = data.configUpdate
        setConfig(prev => ({
          ...prev,
          [u.fieldId]: { value: u.newValue, reason: u.newReason }
        }))
      }
    } catch (err) {
      appendMsg('ai', `⚠ ${err.message}`)
    }
  }

  function handleFollowUp(fieldId, label, value, reason) {
    setActiveField({ fieldId, label, value, reason })
  }

  // ── Clear everything ───────────────────────────────────────────────────────
  function handleClear() {
    setPhase(PHASE_WELCOME)
    setSession(null)
    setSchema(null)
    setConfig(null)
    setMessages([])
    setActiveField(null)
    setChatDisabled(true)
    setError('')
    setChatSliding(false)
    setConfigVisible(false)
    setRightVisible(false)
  }

  // ── Transition styles ──────────────────────────────────────────────────────
  const chatStyle = {
    flex: phase === PHASE_DONE ? 0 : 1,
    width: phase === PHASE_DONE ? 0 : undefined,
    overflow: 'hidden',
    opacity: chatSliding ? 0 : 1,
    transform: chatSliding ? 'translateX(-40px)' : 'translateX(0)',
    transition: 'opacity 0.4s ease, transform 0.4s ease, flex 0.5s ease, width 0.5s ease',
    display: 'flex',
    flexDirection: 'column',
    borderRight: `1px solid ${C.border}`,
    background: C.bgBase,
    pointerEvents: phase === PHASE_DONE ? 'none' : 'all',
  }

  const configStyle = {
    flex: configVisible ? 1 : 0,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
    opacity: configVisible ? 1 : 0,
    transform: configVisible ? 'translateX(0)' : 'translateX(40px)',
    transition: 'opacity 0.5s cubic-bezier(0.22,1,0.36,1) 0.1s, transform 0.5s cubic-bezier(0.22,1,0.36,1) 0.1s, flex 0.5s ease',
    borderRight: `1px solid ${C.border}`,
    background: C.bgBase,
  }

  const rightStyle = {
    width: rightVisible ? 320 : 0,
    minWidth: rightVisible ? 320 : 0,
    opacity: rightVisible ? 1 : 0,
    overflow: 'hidden',
    flexShrink: 0,
    display: 'flex',
    flexDirection: 'column',
    transition: 'width 0.55s cubic-bezier(0.4,0,0.2,1), min-width 0.55s ease, opacity 0.4s ease 0.25s',
    borderLeft: `1px solid ${C.border}`,
    background: C.bgPanel,
  }

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', fontFamily: "'Inter', sans-serif", background: C.bgBase }}>

      {/* Left panel — always visible */}
      <LeftPanel
        session={session}
        onSubmit={handleSubmit}
        onClear={handleClear}
      />

      {/* Centre: chat panel (phase 1) */}
      <div style={chatStyle}>
        <ChatPanel
          messages={messages}
          onSend={handleSend}
          disabled={chatDisabled}
          phase="centre"
        />
      </div>

      {/* Centre: config panel (phase 2) */}
      <div style={configStyle}>
        <ConfigPanel
          schema={schema}
          config={config}
          activeFieldId={activeField?.fieldId}
          onFollowUp={handleFollowUp}
        />
      </div>

      {/* Right: chat panel (phase 2) */}
      <div style={rightStyle}>
        <ChatPanel
          messages={messages}
          onSend={handleSend}
          disabled={false}
          phase="right"
          activeField={activeField}
        />
      </div>
    </div>
  )
}
