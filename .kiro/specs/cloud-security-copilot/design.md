# Design Document: Cloud Security Copilot

## Overview

The Cloud Security Copilot is a GenAI-powered AWS security configuration advisor that generates tailored recommendations based on company-specific business context. The system extracts business intent from natural language descriptions, computes deterministic priority weights for security/compliance/cost trade-offs, fetches real-time AWS service schemas, classifies fields based on computed priorities, and generates configurations with compliance-grounded inline reasoning.

The core innovation is the separation of concerns: AI handles natural language understanding and recommendation generation, while deterministic Python code enforces the security-first priority hierarchy mathematically. This ensures security requirements can never be compromised by AI hallucination or prompt manipulation.

The system supports conversational follow-up where users can ask deeper questions or challenge recommendations. All responses are grounded in authoritative compliance documentation stored in S3, with specific clause citations included in explanations.

### Key Design Principles

1. **Security Priority Enforcement**: Security weight has a mathematical floor of 0.40 that cannot be violated regardless of input
2. **Deterministic Weight Computation**: Priority weights are computed in pure Python with no AI involvement
3. **Pre-Classification Architecture**: Fields are classified and tagged before AI generation, constraining AI behavior
4. **Inline Reasoning Visibility**: All configuration recommendations include visible one-sentence justifications
5. **Compliance Grounding**: Explanations cite specific regulatory clauses from S3-stored compliance documents
6. **Conversational Context Maintenance**: Full conversation history maintained in DynamoDB for coherent multi-turn interactions

## Architecture

### System Components

The system follows a serverless architecture on AWS with clear separation between deterministic logic and AI-powered components.

```
┌─────────────────┐
│  React SPA      │
│  (AWS Amplify)  │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  API Gateway    │
│  (REST API)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              AWS Lambda Functions                   │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐               │
│  │extractIntent │  │ fetchSchema  │               │
│  │              │  │              │               │
│  │ • Bedrock    │  │ • MCP Server │               │
│  │ • weights.py │  │ • Bedrock    │               │
│  │              │  │ • classifier │               │
│  └──────────────┘  └──────────────┘               │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐               │
│  │generateConfig│  │ explainField │               │
│  │              │  │              │               │
│  │ • Bedrock    │  │ • Bedrock    │               │
│  │ • S3 RAG     │  │ • S3 RAG     │               │
│  └──────────────┘  └──────────────┘               │
│                                                      │
│  ┌──────────────┐                                  │
│  │terraformExp. │                                  │
│  │ (stretch)    │                                  │
│  └──────────────┘                                  │
└─────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐
│   DynamoDB      │  │      S3         │
│                 │  │                 │
│ • Sessions      │  │ • Schemas       │
│ • Profiles      │  │ • Compliance    │
│ • Configs       │  │   Docs          │
│ • Conversations │  │                 │
└─────────────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Amazon Bedrock  │
│                 │
│ Claude 3 Sonnet │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  AWS Docs MCP   │
│     Server      │
└─────────────────┘
```

### Component Responsibilities

**Frontend (React SPA)**
- Three-panel interface: intake, configuration display, conversation
- Manages UI state and loading indicators
- Handles user input validation
- Displays inline reasoning with each configuration field
- Maintains active field highlighting during conversations

**API Gateway**
- REST API with five routes
- CORS configuration for cross-origin requests
- Request/response transformation
- Rate limiting and throttling

**Lambda: extractIntent**
- Receives company description text
- Calls Bedrock to extract structured business intent
- Invokes weights_engine.py for deterministic weight computation
- Generates unique session ID
- Stores session data in DynamoDB
- Returns intent profile and computed weights

**Lambda: fetchSchema**
- Checks S3 cache for pre-fetched schemas
- Queries AWS Documentation MCP server via Bedrock if cache miss
- Structures raw documentation into typed field schema
- Retrieves session weights from DynamoDB
- Invokes field_classifier.py to tag each field with instruction and priority
- Caches classified schema to S3
- Returns classified schema with instruction tags

**Lambda: generateConfig**
- Fetches session profile and weights from DynamoDB
- Retrieves relevant compliance document from S3 for context
- Calls Bedrock with field list, instruction tags, and compliance text
- Receives configuration map with value + reason for each field
- Stores configuration in DynamoDB
- Returns configuration with inline reasoning

**Lambda: explainField**
- Fetches full session including conversation history from DynamoDB
- Retrieves relevant compliance document from S3
- Appends user message to conversation history
- Calls Bedrock with full context and compliance grounding
- Parses response for UPDATE_FIELD signal
- Updates DynamoDB with new conversation turn and config changes if applicable
- Returns explanation and optional config update

**Lambda: terraformExport (stretch goal)**
- Fetches session configuration from DynamoDB
- Queries MCP for Terraform resource schema
- Calls Bedrock to generate valid .tf file
- Returns Terraform content as string

**DynamoDB: CopilotSessions**
- Stores session state keyed by sessionId
- Schema: sessionId (PK), companyProfile, computedWeights, selectedService, generatedConfig, conversationHistory, createdAt
- On-demand billing mode
- No TTL (sessions persist for demo duration)

**S3: cloud-copilot-schemas**
- Caches MCP-fetched AWS service schemas
- Path structure: schemas/aws/{service-lowercase}.json
- Reduces MCP query latency on repeated requests
- Pre-populated with S3, RDS, IAM schemas for demo reliability

**S3: cloud-copilot-compliance-docs**
- Stores compliance standard text files
- Path structure: compliance/{framework}-{topic}.txt
- Files: hipaa-encryption.txt, hipaa-access-controls.txt, hipaa-logging.txt, pcidss-access.txt, pcidss-encryption.txt, pcidss-logging.txt, soc2-access.txt, soc2-logging.txt
- Each file contains actual clause text with visible clause numbers

**Amazon Bedrock**
- Model: anthropic.claude-3-sonnet-20240229-v1:0
- Used for: intent extraction, schema structuring, config generation, explanations
- All prompts include strict JSON output requirements
- Retry logic for JSON parsing failures

**AWS Documentation MCP Server**
- Identifier: awslabs.aws-documentation-mcp-server
- Provides real-time AWS service documentation
- Called only from fetchSchema Lambda
- Integrated as Bedrock tool during invoke_model

### Data Flow

**Initial Configuration Generation Flow**
1. User enters company description and selects AWS service
2. Frontend calls POST /intent with description
3. extractIntent Lambda extracts intent via Bedrock, computes weights, stores session
4. Frontend receives sessionId, intent, and weights
5. Frontend calls POST /schema with sessionId and service
6. fetchSchema Lambda checks S3 cache, queries MCP if needed, classifies fields, caches result
7. Frontend receives classified schema with instruction tags
8. Frontend calls POST /config with sessionId and schema
9. generateConfig Lambda fetches compliance docs, calls Bedrock with constraints, stores config
10. Frontend receives configuration map with value + reason per field
11. Frontend displays configuration with inline reasoning visible

**Conversational Follow-Up Flow**
1. User clicks "Ask follow-up" on a field or types a message
2. Frontend calls POST /explain with sessionId, fieldId, currentValue, inlineReason, and message
3. explainField Lambda fetches session and conversation history
4. Lambda retrieves relevant compliance document from S3
5. Lambda appends user message to history and calls Bedrock
6. Bedrock responds with explanation, optionally including UPDATE_FIELD signal
7. Lambda parses response, updates DynamoDB with new turn and config changes
8. Frontend receives explanation and optional configUpdate
9. If configUpdate present, frontend updates both value and reason in UI without reload

## Components and Interfaces

### weights_engine.py

Pure Python module with no external dependencies. Imported by extractIntent Lambda.

**Function**: `compute_weights(intent: dict) -> dict`

**Input Schema**:
```python
{
  "riskTolerance": int,        # 1-5
  "costPressure": int,         # 1-5
  "dataClassification": str,   # "highly-confidential", "confidential", "public"
  "complianceFrameworks": list[str],  # ["HIPAA", "PCI-DSS", "SOC2", "ISO27001"] or []
  "complianceMaturity": str    # "achieved", "in-progress", "not-started"
}
```

**Output Schema**:
```python
{
  "security": float,    # 0.40 to 0.70
  "compliance": float,  # 0.00 to 0.50
  "cost": float         # 0.00 to 0.25
}
# Always sums to 1.0 with tolerance 0.01
```

**Algorithm**:
1. Compute raw security score: base 0.40 + (5 - riskTolerance) * 0.04 + (0.08 if highly-confidential), cap at 0.70
2. Compute raw compliance score: 0.00 if no frameworks, else 0.15 + 0.05 * (len(frameworks) - 1) + maturity_modifier
3. Compute raw cost score: (costPressure / 5) * 0.25, cap at 0.25
4. Normalize: divide each by sum
5. Enforce security floor: if security < 0.40 after normalization, set to 0.40 and subtract deficit from cost then compliance

**Invariants**:
- security >= 0.40 (enforced post-normalization)
- cost <= 0.25 (enforced pre-normalization)
- security + compliance + cost == 1.0 (within 0.01 tolerance)

### field_classifier.py

Pure Python module with no external dependencies. Imported by fetchSchema Lambda.

**Function**: `classify_field(field: dict, weights: dict, active_frameworks: list[str]) -> dict`

**Input Schema**:
```python
field = {
  "fieldId": str,
  "securityRelevance": str,      # "critical", "high", "medium", "low", "none"
  "costRelevance": str,          # "high", "medium", "low", "none"
  "complianceRelevance": list[str],  # ["HIPAA", "PCI-DSS", "SOC2"]
  # ... other field properties
}
weights = {
  "security": float,
  "compliance": float,
  "cost": float
}
active_frameworks = ["HIPAA"]  # from company profile
```

**Output Schema**:
```python
{
  # ... all original field properties
  "instruction": str,           # "LOCKED_SECURE", "PREFER_SECURE", "OPTIMISE_COST", "BALANCED"
  "effectivePriority": float,   # 0.0 to 1.0
  "complianceActive": bool      # True if field's complianceRelevance overlaps active_frameworks
}
```

**Algorithm**:
1. Check compliance_hit: any(f in active_frameworks for f in field.complianceRelevance)
2. Compute effective_priority:
   - Add weights.security * 1.0 if securityRelevance == "critical"
   - Add weights.security * 0.7 if securityRelevance == "high"
   - Add weights.security * 0.4 if securityRelevance == "medium"
   - Add weights.compliance * 0.8 if compliance_hit
   - Add weights.cost * 1.0 if costRelevance == "high"
   - Add weights.cost * 0.5 if costRelevance == "medium"
3. Apply compliance boost: multiply effective_priority by 1.6 if maturity "in-progress", 1.4 if "not-started"
4. Assign instruction tag:
   - "LOCKED_SECURE" if securityRelevance == "critical"
   - "PREFER_SECURE" if securityRelevance == "high" and weights.security > 0.50
   - "OPTIMISE_COST" if costRelevance == "high" and weights.cost > 0.15 and securityRelevance == "none"
   - "BALANCED" otherwise

**Invariants**:
- instruction is always one of the four defined tags
- effectivePriority >= 0.0
- complianceActive == True iff overlap exists between field and active frameworks

### API Contracts

**POST /intent**

Request:
```json
{
  "description": "string (max 5000 chars)"
}
```

Response (200):
```json
{
  "sessionId": "uuid-string",
  "intent": {
    "industry": "string",
    "complianceFrameworks": ["string"],
    "complianceMaturity": "string",
    "teamSize": "string",
    "costPressure": 1-5,
    "riskTolerance": 1-5,
    "missionCriticalServices": ["string"],
    "dataClassification": "string",
    "weightReasoning": "string"
  },
  "weights": {
    "security": 0.0-1.0,
    "compliance": 0.0-1.0,
    "cost": 0.0-1.0
  }
}
```

Error (400):
```json
{
  "error": "Description is required and must not be empty"
}
```

**POST /schema**

Request:
```json
{
  "service": "string",
  "provider": "aws",
  "sessionId": "uuid-string"
}
```

Response (200):
```json
{
  "schema": {
    "provider": "aws",
    "service": "string",
    "fields": [
      {
        "fieldId": "string",
        "label": "string",
        "type": "boolean|string|select|integer",
        "options": ["string"] | null,
        "required": true|false,
        "securityRelevance": "critical|high|medium|low|none",
        "costRelevance": "high|medium|low|none",
        "complianceRelevance": ["string"],
        "aiExplainable": true|false,
        "instruction": "LOCKED_SECURE|PREFER_SECURE|OPTIMISE_COST|BALANCED",
        "effectivePriority": 0.0-1.0,
        "complianceActive": true|false
      }
    ]
  }
}
```

**POST /config**

Request:
```json
{
  "sessionId": "uuid-string",
  "schema": { /* full schema object */ },
  "service": "string"
}
```

Response (200):
```json
{
  "config": {
    "fieldId": {
      "value": true|false|"string"|number,
      "reason": "string (one sentence, company-specific, compliance-cited)"
    }
  }
}
```

**POST /explain**

Request:
```json
{
  "sessionId": "uuid-string",
  "fieldId": "string",
  "fieldLabel": "string",
  "currentValue": any,
  "inlineReason": "string",
  "message": "string"
}
```

Response (200):
```json
{
  "response": "string (3-4 sentences max)",
  "configUpdate": {
    "fieldId": "string",
    "newValue": any,
    "newReason": "string"
  } | null
}
```

**POST /terraform**

Request:
```json
{
  "sessionId": "uuid-string"
}
```

Response (200):
```json
{
  "terraformContent": "string (valid .tf file content)"
}
```

### Frontend Component Interfaces

**IntakePanel**

Props:
```typescript
{
  onSubmit: (description: string, service: string) => void,
  session: {
    sessionId: string,
    intent: object,
    weights: { security: number, compliance: number, cost: number }
  } | null
}
```

State:
- description: string
- selectedService: string

**ConfigPanel**

Props:
```typescript
{
  schema: { provider: string, service: string, fields: Field[] } | null,
  config: { [fieldId: string]: { value: any, reason: string } } | null,
  activeField: string | null,
  onFollowUp: (fieldId: string, fieldLabel: string, currentValue: any, reason: string) => void
}
```

Renders fields grouped by securityRelevance:
- Group 1: critical (red header)
- Group 2: high (amber header)
- Group 3: other (gray header)

Each field displays:
- fieldId (monospace) + "tailored" badge if aiExplainable
- label (human readable)
- value (bold, color-coded)
- reason (italic, always visible)
- "Ask follow-up" button if aiExplainable

**ExplainPanel**

Props:
```typescript
{
  conversation: Array<{ role: "user"|"assistant", content: string, fieldId: string }>,
  onSend: (message: string) => void
}
```

State:
- inputMessage: string

Renders conversation thread with user/AI messages and input area pinned at bottom.

## Data Models

### DynamoDB: CopilotSessions Table

**Primary Key**: sessionId (String)

**Attributes**:
```json
{
  "sessionId": "uuid-string",
  "companyProfile": {
    "industry": "string",
    "complianceFrameworks": ["string"],
    "complianceMaturity": "string",
    "teamSize": "string",
    "costPressure": 1-5,
    "riskTolerance": 1-5,
    "missionCriticalServices": ["string"],
    "dataClassification": "string",
    "weightReasoning": "string"
  },
  "computedWeights": {
    "security": 0.0-1.0,
    "compliance": 0.0-1.0,
    "cost": 0.0-1.0
  },
  "selectedService": "string",
  "generatedConfig": {
    "fieldId": {
      "value": any,
      "reason": "string"
    }
  },
  "conversationHistory": [
    {
      "role": "user|assistant",
      "content": "string",
      "fieldId": "string"
    }
  ],
  "createdAt": 1234567890
}
```

**Access Patterns**:
- GetItem by sessionId (all Lambda functions)
- PutItem on session creation (extractIntent)
- UpdateItem to add config (generateConfig)
- UpdateItem to append conversation (explainField)

### S3: Schema Cache

**Bucket**: cloud-copilot-schemas

**Object Key Pattern**: schemas/aws/{service-lowercase}.json

**Object Content**:
```json
{
  "provider": "aws",
  "service": "S3",
  "fields": [
    {
      "fieldId": "BlockPublicAcls",
      "label": "Block public ACLs",
      "type": "boolean",
      "options": null,
      "required": true,
      "securityRelevance": "critical",
      "costRelevance": "none",
      "complianceRelevance": ["HIPAA", "PCI-DSS", "SOC2"],
      "aiExplainable": true,
      "instruction": "LOCKED_SECURE",
      "effectivePriority": 0.931,
      "complianceActive": true
    }
  ]
}
```

**Access Patterns**:
- GetObject by service name (fetchSchema)
- PutObject after MCP fetch and classification (fetchSchema)

### S3: Compliance Documents

**Bucket**: cloud-copilot-compliance-docs

**Object Key Pattern**: compliance/{framework}-{topic}.txt

**Files**:
- hipaa-encryption.txt
- hipaa-access-controls.txt
- hipaa-logging.txt
- pcidss-access.txt
- pcidss-encryption.txt
- pcidss-logging.txt
- soc2-access.txt
- soc2-logging.txt

**Object Content Format**:
```
HIPAA Security Rule §164.312(e)(2)(ii)

Encryption and Decryption (Addressable)

Implement a mechanism to encrypt and decrypt electronic protected 
health information.

[2-3 paragraphs of actual clause text with visible clause numbers]
```

**Access Patterns**:
- GetObject by framework + topic mapping (generateConfig, explainField)
- Mapping logic: field.complianceRelevance + field category (encryption/access/logging) → filename

### Bedrock Prompt Templates

**Intent Extraction Prompt**:
```
Extract structured business context from this company description. 
Return ONLY valid JSON with these exact fields:
- industry (string)
- complianceFrameworks (array of strings: HIPAA, PCI-DSS, SOC2, ISO27001, or empty)
- complianceMaturity (string: achieved, in-progress, not-started)
- teamSize (string: small, medium, large)
- costPressure (integer 1-5, where 5 is highest pressure)
- riskTolerance (integer 1-5, where 1 is lowest tolerance)
- missionCriticalServices (array of strings)
- dataClassification (string: highly-confidential, confidential, public)
- weightReasoning (one sentence explaining the company profile)

Hard rules:
- costPressure and riskTolerance must be integers 1 to 5
- complianceFrameworks must be an array even if empty
- If no compliance mentioned, use empty array []
- Return ONLY the JSON object, no preamble

Company description:
{description}
```

**Schema Structuring Prompt**:
```
From this AWS documentation, extract ALL configuration fields for {service}. 
Return ONLY a JSON object:
{
  "provider": "aws",
  "service": "{service}",
  "fields": [
    {
      "fieldId": "exact AWS API parameter name",
      "label": "human readable label",
      "type": "boolean|string|select|integer",
      "options": ["array of allowed values if select"] | null,
      "required": true|false,
      "securityRelevance": "critical|high|medium|low|none",
      "costRelevance": "high|medium|low|none",
      "complianceRelevance": ["HIPAA", "PCI-DSS", "SOC2", "ISO27001"],
      "aiExplainable": true if wrong value creates security or cost risk else false
    }
  ]
}

Rules:
- fieldId must be the EXACT AWS API parameter name
- Return ONLY the JSON, no explanation

AWS Documentation:
{mcp_docs}
```

**Config Generation Prompt**:
```
You are configuring AWS {service} for a specific company.

ENFORCED priority weights — computed by backend, do not override:
Security: {weights.security}
Compliance: {weights.compliance}
Cost: {weights.cost}

Company profile:
Industry: {intent.industry}
Compliance: {frameworks} ({maturity})
Cost pressure: {costPressure}/5
Risk tolerance: {riskTolerance}/5
Weight reasoning: {weightReasoning}

Compliance reference text:
{compliance_text}

Fields to configure:
{json_fields_with_instructions}

Return ONLY a JSON object where each key is a fieldId and each value is an object with exactly two keys:
  "value": the recommended setting (boolean, string, or number)
  "reason": one sentence — must be specific to this company, must cite compliance clause number if reference text contains a relevant one, never generic

Critical rules:
- LOCKED_SECURE fields: most secure value, zero exceptions
- PREFER_SECURE fields: secure value strongly preferred
- OPTIMISE_COST fields: cost-efficient option permitted
- BALANCED fields: use judgement based on profile
- Security is NEVER relaxed for cost reasons
- BAD reason: "Encryption is important for security"
- GOOD reason: "HIPAA §164.312(e)(2)(ii) requires encryption of ePHI for your patient data workload"
```

**Explanation System Prompt**:
```
You are a cloud security advisor for a {industry} company configuring AWS {service}.

Company context:
Compliance: {frameworks} ({maturity})
Cost pressure: {costPressure}/5
Risk tolerance: {riskTolerance}/5
Security weight: {security} — never compromise this

Compliance reference:
{compliance_text}

The user has already seen this inline explanation:
{inlineReason}

They are now asking a follow-up question or pushing back.
Respond to their specific concern with full context.

Rules:
1. Do not repeat the inline reason — the user already read it. Go deeper or address their specific concern directly.
2. Always tie response to THIS company's specific context.
3. If field is LOCKED_SECURE and user wants to relax it, explain why it cannot change and suggest a safe alternative.
4. If user has a valid reason and field allows adjustment, suggest the best alternative.
5. If recommending a field value change, end with:
   UPDATE_FIELD: {"fieldId": "...", "newValue": ..., "newReason": "..."}
   newReason must be a one-sentence explanation of the new value.
6. If no change needed, do not include UPDATE_FIELD at all.
7. Keep responses to 3-4 sentences maximum.
8. Never give generic advice.
```

