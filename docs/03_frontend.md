# Frontend — Cloud Security Copilot

## Overview

The frontend is a React single-page application with three panels
side by side. It talks to the backend via fetch() calls to either
localhost:5000 (development) or the API Gateway URL (production).
Deployed on AWS Amplify.

---

## Layout — Three Panels

```
|  Left Panel   |    Centre Panel     |  Right Panel  |
|   280px wide  |    fills remaining  |   320px wide  |
|               |                     |               |
| Company       | Configuration form  | Conversation  |
| profile       | real AWS field      | panel for     |
| intake        | names, values,      | follow-up     |
|               | inline reasons      | questions     |
```

---

## Key Design Decision — Inline Reasons, No Why? Button

Every field shows its reason immediately — no button to click
to discover why. The user sees:

  Field name (monospace)          [tailored badge]
  Human readable label
  Recommended value
  "One sentence reason specific to this company"
                              [Ask follow-up ↗]

The reason is not hidden. It is the primary explanation and
always visible. The Ask follow-up button is for deeper
questions or pushback — not for the basic why.

This eliminates doubt. The user reads the recommendation and
the justification together without any extra action.

---

## API Contract

### POST /intent
Request: { description: string }
Response: {
  sessionId: string,
  intent: {
    industry: string,
    complianceFrameworks: array of strings,
    complianceMaturity: string,
    teamSize: string,
    costPressure: number,
    riskTolerance: number,
    missionCriticalServices: array of strings,
    dataClassification: string,
    weightReasoning: string
  },
  weights: {
    security: number,
    compliance: number,
    cost: number
  }
}

### POST /schema
Request: { service: string, provider: string, sessionId: string }
Response: {
  schema: {
    provider: string,
    service: string,
    fields: array of {
      fieldId: string,
      label: string,
      type: string,
      options: array or null,
      required: boolean,
      securityRelevance: string,
      costRelevance: string,
      complianceRelevance: array of strings,
      aiExplainable: boolean,
      instruction: string,
      effectivePriority: number,
      complianceActive: boolean
    }
  }
}

### POST /config
Request: { sessionId: string, schema: object, service: string }
Response: {
  config: object where each key is a fieldId and each value is:
  {
    value: boolean or string or number,
    reason: string (one sentence, company-specific)
  }
}

### POST /explain
Request: {
  sessionId: string,
  fieldId: string,
  fieldLabel: string,
  currentValue: any,
  inlineReason: string,
  message: string (user's typed follow-up or pushback)
}
Response: {
  response: string,
  configUpdate: null or { fieldId, newValue, newReason }
}

### POST /terraform (stretch goal)
Request: { sessionId: string }
Response: { terraformContent: string }

---

## Mock Data for Development

Use this while backend is not ready.
Replace with real API calls in hour 6.

Mock session (from /intent):
```javascript
const MOCK_SESSION = {
  sessionId: "mock-session-123",
  intent: {
    industry: "healthcare",
    complianceFrameworks: ["HIPAA"],
    complianceMaturity: "in-progress",
    teamSize: "small",
    costPressure: 2,
    riskTolerance: 1,
    missionCriticalServices: ["S3", "RDS"],
    dataClassification: "highly-confidential",
    weightReasoning: "Healthcare company under active HIPAA programme requires maximum security priority"
  },
  weights: { security: 0.62, compliance: 0.28, cost: 0.10 }
}
```

Mock schema (from /schema):
```javascript
const MOCK_SCHEMA = {
  schema: {
    provider: "aws", service: "S3",
    fields: [
      { fieldId: "BlockPublicAcls", label: "Block public ACLs",
        type: "boolean", options: null, required: true,
        securityRelevance: "critical", costRelevance: "none",
        complianceRelevance: ["HIPAA","PCI-DSS","SOC2"],
        aiExplainable: true, instruction: "LOCKED_SECURE",
        effectivePriority: 0.931, complianceActive: true },
      { fieldId: "ServerSideEncryptionConfiguration",
        label: "Server-side encryption", type: "select",
        options: ["None","SSE-S3 (AES-256)","SSE-KMS"],
        required: true, securityRelevance: "critical",
        costRelevance: "medium",
        complianceRelevance: ["HIPAA","PCI-DSS"],
        aiExplainable: true, instruction: "LOCKED_SECURE",
        effectivePriority: 0.887, complianceActive: true },
      { fieldId: "VersioningConfiguration",
        label: "Versioning", type: "select",
        options: ["Enabled","Suspended"], required: false,
        securityRelevance: "high", costRelevance: "medium",
        complianceRelevance: ["SOC2"],
        aiExplainable: true, instruction: "PREFER_SECURE",
        effectivePriority: 0.644, complianceActive: false },
      { fieldId: "LoggingConfiguration",
        label: "Server access logging", type: "boolean",
        options: null, required: false,
        securityRelevance: "medium", costRelevance: "low",
        complianceRelevance: ["HIPAA","SOC2"],
        aiExplainable: true, instruction: "PREFER_SECURE",
        effectivePriority: 0.521, complianceActive: true },
      { fieldId: "LifecycleConfiguration",
        label: "Lifecycle rules", type: "boolean",
        options: null, required: false,
        securityRelevance: "none", costRelevance: "high",
        complianceRelevance: [],
        aiExplainable: true, instruction: "OPTIMISE_COST",
        effectivePriority: 0.100, complianceActive: false }
    ]
  }
}
```

Mock config (from /config) — IMPORTANT: every field has
value AND reason:
```javascript
const MOCK_CONFIG = {
  config: {
    BlockPublicAcls: {
      value: true,
      reason: "Your patient records bucket must block public access under HIPAA §164.312 — no exceptions for PHI storage."
    },
    ServerSideEncryptionConfiguration: {
      value: "SSE-KMS",
      reason: "HIPAA §164.312(e)(2)(ii) requires encryption of ePHI — KMS gives you the audit trail your compliance programme needs."
    },
    VersioningConfiguration: {
      value: "Enabled",
      reason: "SOC2 CC6.1 requires version control on data stores — enables recovery from accidental deletion."
    },
    LoggingConfiguration: {
      value: true,
      reason: "HIPAA §164.312(b) mandates audit controls on all ePHI — access logs are your compliance evidence."
    },
    LifecycleConfiguration: {
      value: false,
      reason: "Lifecycle rules could move PHI to storage classes that may not meet HIPAA encryption requirements."
    }
  }
}
```

---

## App.jsx — State Management

### State variables
- session: null or { sessionId, intent, weights }
- schema: null or the full schema object
- config: null or { fieldId: {value, reason} } map
- conversation: array of { role, content, fieldId }
- activeField: null or string fieldId
- loading: empty string or loading message string

### Flow
1. User submits → handleSubmit() called
2. handleSubmit calls /intent → sets session
3. handleSubmit calls /schema → sets schema
4. handleSubmit calls /config → sets config, clears conversation
5. User clicks Ask follow-up → handleFollowUp() called
6. handleFollowUp sets activeField, appends message to
   conversation, calls /explain, appends response,
   applies configUpdate if present
7. User sends another message → handleFollowUp() called again

### Loading states
"Analysing company profile..."
  shown while /intent is in flight

"Fetching {service} field names via AWS Docs MCP..."
  shown while /schema is in flight

"Generating tailored recommendations..."
  shown while /config is in flight

Show full-screen centered loading message.
Hide all panels while loading.

### Config update handling
When /explain returns configUpdate that is not null:
  setConfig(prev => ({
    ...prev,
    [configUpdate.fieldId]: {
      value: configUpdate.newValue,
      reason: configUpdate.newReason
    }
  }))
This updates BOTH the value and the inline reason live
in the centre panel without any page reload.

---

## IntakePanel Component

### Props
- onSubmit: function(description, service)
- session: null or session object

### What it renders

Top section:
- Heading "Company profile" 16px bold
- Large textarea for company description
  Placeholder: "Describe your company — industry, compliance
  needs, team size, cost sensitivity, what makes security
  critical or not..."
  8 rows minimum

- Service selector dropdown with options:
    S3 — Simple Storage Service
    RDS — Relational Database Service
    EC2 — Virtual Machines
    IAM — Identity and Access Management
    Lambda — Serverless Functions
    ElastiCache — Caching Service
    CloudFront — Content Delivery Network
    ECS — Container Service

- Submit button: "Analyse and generate config"
  Full width, dark blue #1B3A5C, white text

Bottom section (only when session is not null):
- Light blue card showing extracted profile
- Industry, compliance frameworks, maturity
- Three weight numbers:
  Security: {session.weights.security}
  Compliance: {session.weights.compliance}
  Cost: {session.weights.cost}
- weightReasoning in small italic text below

### Width
280px fixed, full height, right border 1px solid #eee

---

## ConfigPanel Component

### Props
- schema: null or schema object
- config: null or { fieldId: {value, reason} } map
- activeField: null or string
- onFollowUp: function(fieldId, fieldLabel, currentValue, reason)

### Empty state
"Select a service and analyse your company profile to see
tailored configuration recommendations."

### Field grouping — render in this order
Group 1 — Security — critical
  Header background: #FDEAEA, text: #8B1A1A

Group 2 — Security — high
  Header background: #FFF3D6, text: #7A4A00

Group 3 — Other settings
  Header background: #F5F5F5, text: #555555

### Each field renders as a card containing

Row 1 — field identifier line:
  Left: fieldId in monospace 12px dark blue (#1B3A5C)
  Left: "tailored" badge in purple if aiExplainable is true
        Badge: background #EEEDFE, text #534AB7, 10px, pill
  Right: recommended value
         true → bold green (#1A6B3C)
         false → bold red (#8B1A1A)
         string → bold dark (#333333)

Row 2 — label:
  Field's human readable label in 11px muted gray

Row 3 — inline reason (ALWAYS VISIBLE, no click needed):
  The reason string from config[fieldId].reason
  Shown in 12px italic, color #555555
  This is the primary explanation — always shown
  Example: "HIPAA §164.312(e)(2)(ii) requires encryption
            of ePHI — KMS gives you the audit trail your
            compliance programme needs."

Row 4 — ask follow-up button:
  Only shown if aiExplainable is true
  Text: "Ask follow-up ↗"
  Small, right-aligned, blue text (#2E6DA4), no background
  On click: calls onFollowUp(fieldId, label, value, reason)
  This is for deeper questions or pushback — not for
  the basic why (which is already shown in row 3)

Active field highlight:
  When activeField matches fieldId, set card background
  to light blue (#EEF4FF)

Each field card:
  Background: white
  Border bottom: 1px solid #f0f0f0
  Padding: 12px 16px

### Panel header
"{service} configuration" in 14px bold dark blue
Below header comes the grouped field list

### Width
Fills remaining space, full height
Left and right borders 1px solid #eee
overflow-y auto

---

## ExplainPanel Component

### Props
- conversation: array of { role, content, fieldId }
- onSend: function(message)

### What it renders

Top header: "Follow-up questions" in 14px bold dark blue

Middle — conversation thread (scrollable):
  Empty state: "Click 'Ask follow-up' on any field to ask
  a deeper question or push back on a recommendation."

  Each message:
    User: light gray background (#F5F5F5)
    AI: white background
    Both: 1px solid #eee border, border-radius 8px, 13px text
    Role label: "You" or "AI advisor" in 11px bold gray
    If message has fieldId: show "· {fieldId}" next to label

Bottom — input area:
  Input placeholder: "Ask a deeper question or push back..."
  Send button: dark blue background
  On Enter key: call onSend(input) and clear input
  On Send click: same

### Width
320px fixed, full height, left border 1px solid #eee
Flex column so input stays pinned at bottom

---

## Styling Guidelines

Font: Arial, sans-serif
No external CSS libraries — inline styles only
Primary dark blue: #1B3A5C
Secondary blue: #2E6DA4
Success green: #1A6B3C (true values)
Danger red: #8B1A1A (false values, critical section)
Warning amber: #7A4A00 (high severity section)
Purple badge text: #534AB7
Purple badge background: #EEEDFE
Reason text: #555555 italic
Border: #eeeeee
Active field: #EEF4FF background

---

## Deployment — AWS Amplify

From the frontend folder after core is tested:

npm install -g @aws-amplify/cli
amplify configure
amplify init
amplify add hosting
amplify publish

Switch API constant in App.jsx from localhost:5000 to
API Gateway URL before running amplify publish.

---

## Development Order for Person 3

Hour 1-2: ConfigPanel with mock data.
  Get all field rows rendering correctly.
  Get inline reason showing under every field value.
  Get Ask follow-up button on aiExplainable fields.
  Get active field highlight working.
  Get section grouping by securityRelevance working.

Hour 3-4: ExplainPanel.
  Get conversation thread rendering.
  Get input and send working (log to console for now).

Hour 5: IntakePanel.
  Get description textarea and service selector working.
  Get extracted profile card showing weights and reasoning.

Hour 5-6: Wire App.jsx.
  Connect all three panels with mock data.
  Implement handleSubmit and handleFollowUp.
  Config update (value + reason together) working on mock.

Hour 6: Integration with real backend.
  Replace all mock returns with real fetch() calls.
  Verify config[fieldId].value and config[fieldId].reason
  both render correctly from real API responses.
  Verify configUpdate updates both value and reason live.

Hour 7: Fix integration bugs.

Hour 8: Deploy to Amplify.
