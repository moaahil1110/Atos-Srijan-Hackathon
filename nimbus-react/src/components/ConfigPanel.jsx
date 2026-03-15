import { C, css } from '../styles'

const GROUPS = [
  { key: 'critical', label: 'Critical security', match: f => f.securityRelevance === 'critical', bg: '#FDEDEC', color: '#C0392B', border: '#C0392B' },
  { key: 'high',     label: 'High security',     match: f => f.securityRelevance === 'high',     bg: '#FEF9E7', color: '#D68910', border: '#D68910' },
  { key: 'other',    label: 'Other settings',    match: () => true,                              bg: C.bgPanel, color: C.textMuted, border: C.borderLight },
]

export default function ConfigPanel({ schema, config, activeFieldId, onFollowUp }) {
  if (!schema || !config) return (
    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: C.bgBase }}>
      <p style={{ fontSize: 13, color: C.textFaint }}>Loading configuration...</p>
    </div>
  )

  const fields = schema.fields || []
  const used   = new Set()

  const grouped = GROUPS.map(g => {
    const matched = fields.filter(f => !used.has(f.fieldId) && g.match(f))
    matched.forEach(f => used.add(f.fieldId))
    return { ...g, fields: matched }
  }).filter(g => g.fields.length > 0)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: C.bgBase }}>

      {/* Header */}
      <div style={{ padding: '20px 24px 16px', background: C.navy, borderBottom: `1px solid ${C.border}`, flexShrink: 0 }}>
        <p style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: C.orange, margin: '0 0 4px' }}>Configuration</p>
        <h2 style={{ fontSize: 20, fontWeight: 700, color: '#fff', margin: 0 }}>{schema.service} settings</h2>
      </div>

      {/* Fields */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 28px' }}>
        {grouped.map(group => (
          <div key={group.key} style={{ marginBottom: 32 }}>
            {/* Group header */}
            <div style={{ display: 'inline-block', background: group.bg, color: group.color, borderLeft: `3px solid ${group.border}`, fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', padding: '4px 10px', marginBottom: 14, borderRadius: '0 4px 4px 0' }}>
              {group.label}
            </div>

            {group.fields.map(field => (
              <FieldCard
                key={field.fieldId}
                field={field}
                entry={config[field.fieldId]}
                isActive={activeFieldId === field.fieldId}
                onFollowUp={onFollowUp}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}

function FieldCard({ field, entry, isActive, onFollowUp }) {
  const val    = entry?.value
  const reason = entry?.reason || ''

  function renderValue() {
    if (val === true)  return <span style={{ fontWeight: 700, fontSize: 13, color: C.green }}>Enabled</span>
    if (val === false) return <span style={{ fontWeight: 700, fontSize: 13, color: C.red }}>Disabled</span>
    return <span style={{ fontWeight: 700, fontSize: 13, color: C.textPrimary }}>{String(val ?? '—')}</span>
  }

  return (
    <div style={{ ...css.fieldCard, background: isActive ? '#FFF8F0' : '#fff', borderColor: isActive ? C.orange : C.border, marginBottom: 10 }}>

      {/* Row 1 — fieldId + badge + value + follow-up */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, fontWeight: 500, color: C.textPrimary }}>{field.fieldId}</span>
          {field.aiExplainable && (
            <span style={css.tailoredBadge}>tailored</span>
          )}
          {renderValue()}
        </div>
        {field.aiExplainable && (
          <button onClick={() => onFollowUp(field.fieldId, field.label, val, reason)}
            style={{ background: 'none', border: 'none', color: C.orange, fontSize: 11, fontWeight: 600, cursor: 'pointer', whiteSpace: 'nowrap', padding: 0, fontFamily: 'inherit' }}>
            Ask follow-up ↗
          </button>
        )}
      </div>

      {/* Row 2 — label */}
      <p style={{ fontSize: 11, color: C.textFaint, textTransform: 'uppercase', letterSpacing: '0.04em', margin: 0 }}>{field.label}</p>

      {/* Row 3 — inline reason */}
      {reason && (
        <p style={{ fontSize: 13, fontStyle: 'italic', color: C.textMuted, margin: 0, lineHeight: 1.5 }}>{reason}</p>
      )}
    </div>
  )
}
