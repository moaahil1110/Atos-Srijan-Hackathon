// ── ONE line to change before Amplify deploy ──────────────────────────────
export const API_BASE = 'http://localhost:8000'
// swap ↑ to your API Gateway URL before running: amplify publish

const post = async (path, body) => {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })
  if (!res.ok) throw new Error(`${path} returned ${res.status}`)
  return res.json()
}

export const extractIntent  = (description, service)               => post('/intent',  { description, service })
export const fetchSchema    = (service, sessionId)                  => post('/schema',  { service, provider: 'aws', sessionId })
export const generateConfig = (sessionId, schema, service)          => post('/config',  { sessionId, schema, service })
export const explainField   = (sessionId, fieldId, fieldLabel, currentValue, inlineReason, message) =>
  post('/explain', { sessionId, fieldId, fieldLabel, currentValue, inlineReason, message })
