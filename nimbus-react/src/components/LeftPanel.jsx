import { useState } from 'react'
import { C } from '../styles'

const SERVICES = [
  'S3 — Simple Storage Service',
  'RDS — Relational Database Service',
  'EC2 — Virtual Machines',
  'IAM — Identity and Access Management',
  'Lambda — Serverless Functions',
  'ElastiCache — Caching Service',
  'CloudFront — Content Delivery Network',
  'ECS — Container Service',
]

export default function LeftPanel({ session, onSubmit, onClear }) {
  const [description, setDescription] = useState('')
  const [service,     setService]     = useState('S3 — Simple Storage Service')
  const [tab,         setTab]         = useState('type')
  const [pdfFile,     setPdfFile]     = useState(null)

  function handleSubmit() {
    if (!description.trim() && !pdfFile) return
    const svc = service.split(' ')[0]
    onSubmit(description.trim(), svc)
  }

  function handleClear() {
    setDescription('')
    setPdfFile(null)
    setTab('type')
    onClear()
  }

  return (
    <div style={{ width: 280, minWidth: 280, height: '100%', display: 'flex', flexDirection: 'column', background: C.bgPanel, borderRight: `1px solid ${C.border}` }}>

      {/* Header */}
      <div style={{ padding: '20px 20px 16px', background: C.navy, borderBottom: `1px solid ${C.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: C.orange, margin: '0 0 4px' }}>Nimbus 1000</p>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: '#fff', margin: 0 }}>Company profile</h1>
        </div>
        <button onClick={handleClear} style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: '#fff', fontSize: 11, fontWeight: 600, padding: '6px 12px', borderRadius: 4, cursor: 'pointer', marginTop: 2 }}>
          ↺ Clear
        </button>
      </div>

      {/* Form */}
      <div style={{ padding: 20, flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>

        {/* Description tabs */}
        <div>
          <label style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: C.textMuted, letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>Description</label>
          <div style={{ display: 'flex', gap: 4, marginBottom: 10 }}>
            {['type', 'pdf'].map(t => (
              <button key={t} onClick={() => setTab(t)}
                style={{ flex: 1, padding: '6px 0', fontSize: 11, fontWeight: 600, borderRadius: 4, border: tab === t ? 'none' : `1px solid ${C.border}`, cursor: 'pointer', background: tab === t ? C.navy : '#fff', color: tab === t ? '#fff' : C.textMuted, transition: 'all 0.15s' }}>
                {t === 'type' ? 'Type' : 'Upload PDF'}
              </button>
            ))}
          </div>

          {tab === 'type' ? (
            <textarea value={description} onChange={e => setDescription(e.target.value)} rows={7}
              placeholder="Describe your company — industry, compliance needs, team size, cost sensitivity..."
              style={{ width: '100%', padding: '10px 12px', fontSize: 12, lineHeight: 1.6, border: `1px solid ${C.border}`, borderRadius: 4, resize: 'vertical', fontFamily: 'inherit', color: C.textPrimary, background: '#fff', outline: 'none' }} />
          ) : (
            <PdfUpload file={pdfFile} onFile={setPdfFile} />
          )}
        </div>

        {/* Service selector */}
        <div>
          <label style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: C.textMuted, letterSpacing: '0.06em', display: 'block', marginBottom: 8 }}>AWS Service</label>
          <select value={service} onChange={e => setService(e.target.value)}
            style={{ width: '100%', padding: '8px 10px', fontSize: 12, border: `1px solid ${C.border}`, borderRadius: 4, fontFamily: 'inherit', color: C.textPrimary, background: '#fff', cursor: 'pointer' }}>
            {SERVICES.map(s => <option key={s}>{s}</option>)}
          </select>
        </div>

        {/* Submit */}
        <button onClick={handleSubmit} disabled={!description.trim() && !pdfFile}
          style={{ width: '100%', padding: '11px 0', background: (description.trim() || pdfFile) ? C.orange : C.borderLight, color: '#fff', border: 'none', borderRadius: 4, fontSize: 13, fontWeight: 600, cursor: (description.trim() || pdfFile) ? 'pointer' : 'not-allowed', fontFamily: 'inherit', transition: 'background 0.15s' }}>
          Analyse and generate config
        </button>

        {/* Profile card */}
        {session && <ProfileCard session={session} />}
      </div>
    </div>
  )
}

function PdfUpload({ file, onFile }) {
  const [dragging, setDragging] = useState(false)

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f?.type === 'application/pdf') onFile(f)
  }

  if (file) return (
    <div style={{ background: '#FFF8F0', border: `1px solid #F5CBA7`, borderRadius: 4, padding: '8px 12px', display: 'flex', alignItems: 'center', gap: 8 }}>
      <span style={{ fontSize: 12, color: C.textPrimary, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{file.name}</span>
      <button onClick={() => onFile(null)} style={{ background: 'none', border: 'none', color: C.textFaint, cursor: 'pointer', fontSize: 13 }}>✕</button>
    </div>
  )

  return (
    <div onDragOver={e => { e.preventDefault(); setDragging(true) }}
         onDragLeave={() => setDragging(false)}
         onDrop={handleDrop}
         onClick={() => document.getElementById('pdf-input').click()}
         style={{ border: `2px dashed ${dragging ? C.orange : C.borderLight}`, borderRadius: 4, height: 100, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', background: dragging ? '#FFF8F0' : '#fff', transition: 'all 0.15s' }}>
      <svg width="24" height="24" fill="none" stroke={C.textFaint} strokeWidth="1.5" viewBox="0 0 24 24" style={{ marginBottom: 6 }}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
      </svg>
      <p style={{ fontSize: 12, color: C.textMuted }}>Drop PDF or <span style={{ color: C.orange, fontWeight: 600 }}>browse</span></p>
      <input id="pdf-input" type="file" accept="application/pdf" style={{ display: 'none' }} onChange={e => onFile(e.target.files[0])} />
    </div>
  )
}

function ProfileCard({ session }) {
  const { intent = {}, weights = {} } = session
  return (
    <div style={{ background: '#FFF8F0', border: `1px solid #F5CBA7`, borderRadius: 4, padding: 14, fontSize: 12 }}>
      <p style={{ fontWeight: 700, textTransform: 'uppercase', fontSize: 10, letterSpacing: '0.06em', color: C.navy, marginBottom: 10 }}>Extracted Profile</p>
      <Row label="Industry"   value={intent.industry || '—'} />
      <Row label="Frameworks" value={(intent.complianceFrameworks || []).join(', ') || 'None'} />
      <Row label="Maturity"   value={intent.complianceMaturity || '—'} />
      <Row label="Data"       value={intent.dataClassification || '—'} />
      <div style={{ borderTop: `1px solid #F5CBA7`, marginTop: 10, paddingTop: 10 }}>
        <WeightRow label="Security"   value={weights.security}   color={C.green} />
        <WeightRow label="Compliance" value={weights.compliance} color={C.navy} />
        <WeightRow label="Cost"       value={weights.cost}       color={C.amber} />
      </div>
      {intent.weightReasoning && (
        <p style={{ fontSize: 11, fontStyle: 'italic', color: C.textMuted, marginTop: 8, lineHeight: 1.5 }}>{intent.weightReasoning}</p>
      )}
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5, gap: 8 }}>
      <span style={{ color: C.textMuted, flexShrink: 0 }}>{label}</span>
      <span style={{ color: C.textPrimary, fontWeight: 500, textAlign: 'right' }}>{value}</span>
    </div>
  )
}

function WeightRow({ label, value, color }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
      <span style={{ color: C.textMuted }}>{label}</span>
      <span style={{ fontWeight: 600, color }}>{typeof value === 'number' ? value.toFixed(2) : '—'}</span>
    </div>
  )
}
