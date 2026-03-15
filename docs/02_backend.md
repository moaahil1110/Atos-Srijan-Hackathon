# Backend — Cloud Security Copilot

## Overview

The backend is five AWS Lambda functions sitting behind API
Gateway. Each function has one job. They share data through
DynamoDB and S3. All AI calls go through Amazon Bedrock using
Claude 3 Sonnet. The MCP server is called only from fetchSchema.

No servers to manage. Everything is serverless.

---

## Shared Infrastructure

### DynamoDB Table
Name: CopilotSessions
Partition key: sessionId (String)
Region: ap-south-1 (or ap-southeast-1 — match what Person 2 created)
Billing: On-Demand

What gets stored per session:
- sessionId: unique string generated at intent extraction
- companyProfile: the structured JSON extracted by Bedrock
- computedWeights: {security, compliance, cost} from weight engine
- selectedService: e.g. "S3", "RDS"
- generatedConfig: {fieldId: {value, reason}} map
  IMPORTANT: each field stores BOTH a value and a one-line reason.
  Example:
  {
    "BlockPublicAcls": {
      "value": true,
      "reason": "Your patient records bucket must block public
                 access under HIPAA §164.312 — no exceptions
                 for PHI storage."
    }
  }
- conversationHistory: array of {role, content, fieldId}
- createdAt: unix timestamp

### S3 Buckets
cloud-copilot-schemas — stores MCP-fetched field schemas
  Path structure: schemas/aws/{service-lowercase}.json

cloud-copilot-compliance-docs — stores compliance text files
  Path structure: compliance/{filename}.txt

### Compliance Document Mapping
The explainField Lambda fetches the right file based on:
  active framework + field's complianceRelevance tag

Mapping:
  HIPAA + encryption field   → compliance/hipaa-encryption.txt
  HIPAA + access field       → compliance/hipaa-access-controls.txt
  HIPAA + logging field      → compliance/hipaa-logging.txt
  PCI-DSS + access field     → compliance/pcidss-access.txt
  PCI-DSS + encryption field → compliance/pcidss-encryption.txt
  PCI-DSS + logging field    → compliance/pcidss-logging.txt
  SOC2 + access field        → compliance/soc2-access.txt
  SOC2 + logging field       → compliance/soc2-logging.txt
  No match found             → use empty string, no citation

Each compliance file must contain the actual clause text with
the clause number visible (e.g. §164.312(e)(2)(ii)) so Bedrock
can cite it naturally in inline reasons and explanations.

### Bedrock Model
Model ID: anthropic.claude-3-sonnet-20240229-v1:0
Region: same as all other resources
All Lambda functions use the same model ID.

### Flask Backend (local development)
For local testing before Lambda deployment, run a Flask app
on port 5000. The React frontend points to localhost:5000
during development and to API Gateway URL after deployment.

---

## weights_engine.py

This file is imported by extractIntent Lambda.
Pure Python — no AWS dependencies, no Bedrock calls.
Must be in the same folder as the Lambda handler or shared layer.

### Function signature
compute_weights(intent: dict) -> dict

### Input — intent dict keys used
- riskTolerance: integer 1-5
- costPressure: integer 1-5
- dataClassification: string
- complianceFrameworks: list of strings
- complianceMaturity: string

### Output
{
  "security": float,
  "compliance": float,
  "cost": float
}
Three numbers always summing to exactly 1.0.

### Logic — implement exactly this

Security score:
  Start at 0.40
  Add (5 minus riskTolerance) multiplied by 0.04
  If dataClassification is "highly-confidential" add 0.08
  Cap at 0.70

Compliance score:
  Start at 0.00
  If complianceFrameworks is not empty and not ["none"]:
    Set to 0.15
    Add 0.05 for each additional framework beyond the first
    If complianceMaturity is "in-progress" add 0.10
    If complianceMaturity is "not-started" add 0.05

Cost score:
  Formula: (costPressure divided by 5) multiplied by 0.25

Normalise:
  total = security + compliance + cost
  security = security divided by total
  compliance = compliance divided by total
  cost = cost divided by total
  Round all to 3 decimal places

Final enforcement:
  If security is below 0.40:
    deficit = 0.40 minus security
    security = 0.40
    If cost >= deficit: cost = cost minus deficit
    Else: compliance = compliance minus deficit

Return {security, compliance, cost}

---

## field_classifier.py

This file is imported by fetchSchema Lambda.
Pure Python — no AWS dependencies.

### Function signature
classify_field(field: dict, weights: dict,
               active_frameworks: list) -> dict

### Logic — implement exactly this

Read field's securityRelevance, costRelevance, and
complianceRelevance from the field dict.

Check if any item in field's complianceRelevance is also
in active_frameworks. If yes, compliance_hit = True.

Compute effective_priority score:
  If securityRelevance is "critical": add weights.security * 1.0
  If securityRelevance is "high": add weights.security * 0.7
  If securityRelevance is "medium": add weights.security * 0.4
  If compliance_hit: add weights.compliance * 0.8
  If costRelevance is "high": add weights.cost * 1.0
  If costRelevance is "medium": add weights.cost * 0.5

Assign instruction tag:
  If securityRelevance is "critical":
    instruction = "LOCKED_SECURE"
  Else if securityRelevance is "high" and
          weights.security > 0.50:
    instruction = "PREFER_SECURE"
  Else if costRelevance is "high" and
          weights.cost > 0.15 and
          securityRelevance is "none":
    instruction = "OPTIMISE_COST"
  Else:
    instruction = "BALANCED"

If compliance_hit:
  Multiply effective_priority by 1.6 if maturity in-progress
  Multiply effective_priority by 1.4 if maturity not-started

Return the field dict with these added:
  instruction: string
  effectivePriority: float
  complianceActive: boolean

---

## Lambda 1 — extractIntent

File: backend/extract_intent/handler.py
API route: POST /intent
Triggered by: user submitting company description

### Input (request body)
{
  "description": "We are a healthcare startup..."
}

### What it does step by step

Step 1: Send description to Bedrock with extraction prompt.
Bedrock returns structured JSON profile.

Step 2: Call weights_engine.compute_weights(profile).
Get {security, compliance, cost} weights back.

Step 3: Generate a unique sessionId using uuid4().

Step 4: Save to DynamoDB:
{
  "sessionId": sessionId,
  "companyProfile": profile,
  "computedWeights": weights,
  "conversationHistory": [],
  "createdAt": current unix timestamp
}

Step 5: Return response.

### Output
{
  "sessionId": "uuid-string",
  "intent": { full profile object },
  "weights": { "security": 0.62, "compliance": 0.28,
               "cost": 0.10 }
}

### Bedrock prompt for intent extraction
Tell Bedrock:
"Extract structured business context from this company
description. Return ONLY valid JSON with these exact fields:
industry, complianceFrameworks (array), complianceMaturity,
teamSize, costPressure (1-5 integer), riskTolerance (1-5
integer), missionCriticalServices (array), dataClassification,
weightReasoning (one sentence explaining the company profile).

Hard rules:
- costPressure and riskTolerance must be integers 1 to 5
- complianceFrameworks must be an array even if empty
- If no compliance mentioned, use empty array []
- Return ONLY the JSON object, no preamble"

---

## Lambda 2 — fetchSchema

File: backend/fetch_schema/handler.py
API route: POST /schema
Triggered by: user selecting an AWS service

### Input (request body)
{
  "service": "S3",
  "provider": "aws",
  "sessionId": "uuid-string"
}

### What it does step by step

Step 1: Build cache key as schemas/aws/{service-lowercase}.json.
Check S3 bucket cloud-copilot-schemas for this key.
If found, return immediately — skip all remaining steps.

Step 2: Query Bedrock with MCP tool enabled.
Ask it to search AWS documentation for all configuration
parameters for the requested service.

Step 3: Send the raw docs text back to Bedrock with a
structuring prompt. Ask it to extract a typed field schema.

Step 4: Fetch the session from DynamoDB to get weights and
active compliance frameworks.

Step 5: Run field_classifier.classify_field() on every field.
Tag each with instruction and effectivePriority.

Step 6: Write the final classified schema to S3 cache.

Step 7: Return the classified schema.

### Output
{
  "schema": {
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
}

### Bedrock schema structuring prompt
Tell Bedrock:
"From this AWS documentation, extract ALL configuration fields
for {service}. Return ONLY a JSON object:
{
  provider: aws,
  service: service name,
  fields: array of {
    fieldId: exact AWS API parameter name,
    label: human readable label,
    type: boolean or string or select or integer,
    options: array of allowed values if select else null,
    required: true or false,
    securityRelevance: critical or high or medium or low or none,
    costRelevance: high or medium or low or none,
    complianceRelevance: array of HIPAA PCI-DSS SOC2 ISO27001,
    aiExplainable: true if wrong value creates security or
                   cost risk else false
  }
}
Rules:
- fieldId must be the EXACT AWS API parameter name
- Return ONLY the JSON, no explanation"

---

## Lambda 3 — generateConfig

File: backend/generate_config/handler.py
API route: POST /config
Triggered by: after schema is fetched

### Input (request body)
{
  "sessionId": "uuid-string",
  "schema": { full schema object from fetchSchema },
  "service": "S3"
}

### What it does step by step

Step 1: Fetch session from DynamoDB using sessionId.
Get companyProfile and computedWeights.

Step 2: Fetch compliance document from S3 for context.
Use the company's primary active framework to get the most
relevant compliance text. This grounds the inline reasons
that Bedrock generates per field.

Step 3: Build the field list for Bedrock including instruction
tags, compliance document text, and company profile.

Step 4: Call Bedrock. Bedrock returns a config map where
EVERY field has both a value AND a one-line reason.
The reason is shown inline in the UI — it is not hidden
behind a button. It is the primary explanation.

Step 5: Save the {value, reason} config map to DynamoDB.
Update the session's generatedConfig and selectedService.

Step 6: Return config map.

### Output — CRITICAL: every field must have value AND reason
{
  "config": {
    "BlockPublicAcls": {
      "value": true,
      "reason": "Your patient records bucket must block public
                 access under HIPAA §164.312 — no exceptions
                 for PHI storage."
    },
    "ServerSideEncryptionConfiguration": {
      "value": "SSE-KMS",
      "reason": "HIPAA §164.312(e)(2)(ii) requires encryption
                 of ePHI — KMS gives you the audit trail your
                 compliance programme needs."
    },
    "VersioningConfiguration": {
      "value": "Enabled",
      "reason": "SOC2 CC6.1 requires version control on data
                 stores — enables recovery from accidental
                 deletion of patient records."
    },
    "LoggingConfiguration": {
      "value": true,
      "reason": "HIPAA §164.312(b) mandates audit controls
                 on all ePHI — access logs are your compliance
                 evidence."
    },
    "LifecycleConfiguration": {
      "value": false,
      "reason": "Lifecycle rules could move PHI to storage
                 classes that may not meet HIPAA encryption
                 requirements — disabled for safety."
    }
  }
}

### Bedrock config generation prompt
Tell Bedrock:
"You are configuring AWS {service} for a specific company.

ENFORCED priority weights — computed by backend, do not
override:
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
{compliance_text fetched from S3}

Fields to configure:
{json list of fields with instruction tags}

Return ONLY a JSON object where each key is a fieldId and
each value is an object with exactly two keys:
  value: the recommended setting (boolean, string, or number)
  reason: one sentence — must be specific to this company,
          must cite compliance clause number if reference text
          contains a relevant one, never generic

Critical rules:
- LOCKED_SECURE fields: most secure value, zero exceptions
- PREFER_SECURE fields: secure value strongly preferred
- OPTIMISE_COST fields: cost-efficient option permitted
- BALANCED fields: use judgement based on profile
- Security is NEVER relaxed for cost reasons
- BAD reason: 'Encryption is important for security'
- GOOD reason: 'HIPAA §164.312(e)(2)(ii) requires encryption
                of ePHI for your patient data workload'"

---

## Lambda 4 — explainField

File: backend/explain_field/handler.py
API route: POST /explain
Triggered by: Ask follow-up button or counter-ask message

NOTE: This Lambda handles deeper questions and pushback only.
The inline reason in the config form already shows the basic
why. This Lambda goes deeper when the user wants to challenge
or understand more.

### Input (request body)
{
  "sessionId": "uuid-string",
  "fieldId": "BlockPublicAcls",
  "fieldLabel": "Block public ACLs",
  "currentValue": true,
  "inlineReason": "Your patient records bucket must block...",
  "message": "Can we make an exception for marketing assets?"
}

Note: message is the user's actual typed question.
The __WHY__ sentinel is no longer used — inline reason
has replaced the basic why explanation.

### What it does step by step

Step 1: Fetch full session from DynamoDB.
Get companyProfile, computedWeights, selectedService,
generatedConfig, conversationHistory.

Step 2: Find matching compliance document from S3.
Check field's complianceRelevance against active frameworks.
Fetch matching file. Use empty string if no match.

Step 3: If no conversationHistory exists for this fieldId,
create a synthetic opening exchange using the inline reason:
  {role: "assistant", content: inlineReason, fieldId: fieldId}
This gives Bedrock context about what the user already read.

Step 4: Append user message to conversationHistory.

Step 5: Call Bedrock with full conversation history,
system prompt with company context, and compliance text.

Step 6: Parse Bedrock response for UPDATE_FIELD signal.
If present: display_text = text before UPDATE_FIELD:
            config_update = parse JSON after UPDATE_FIELD:

Step 7: Append AI response to conversationHistory in DynamoDB.
If config_update exists:
  Update generatedConfig[fieldId].value = config_update.newValue
  Update generatedConfig[fieldId].reason = config_update.newReason
  Both value and reason update together in DynamoDB.

Step 8: Return response.

### Output
{
  "response": "For marketing assets without patient data,
               create a separate public bucket...",
  "configUpdate": null
}

Or if AI recommends a change:
{
  "response": "Given your need for public marketing assets...",
  "configUpdate": {
    "fieldId": "BucketName",
    "newValue": "acme-patient-data-private",
    "newReason": "Naming convention distinguishes PHI bucket
                  from separate public marketing bucket."
  }
}

### Bedrock system message for explain
Tell Bedrock:
"You are a cloud security advisor for a {industry} company
configuring AWS {service}.

Company context:
Compliance: {frameworks} ({maturity})
Cost pressure: {costPressure}/5
Risk tolerance: {riskTolerance}/5
Security weight: {security} — never compromise this

Compliance reference:
{compliance_text from S3}

The user has already seen this inline explanation:
{inlineReason}

They are now asking a follow-up question or pushing back.
Respond to their specific concern with full context.

Rules:
1. Do not repeat the inline reason — the user already read it.
   Go deeper or address their specific concern directly.
2. Always tie response to THIS company's specific context.
3. If field is LOCKED_SECURE and user wants to relax it,
   explain why it cannot change and suggest a safe alternative.
4. If user has a valid reason and field allows adjustment,
   suggest the best alternative.
5. If recommending a field value change, end with:
   UPDATE_FIELD: {fieldId, newValue, newReason as JSON}
   newReason must be a one-sentence explanation of the new value.
6. If no change needed, do not include UPDATE_FIELD at all.
7. Keep responses to 3-4 sentences maximum.
8. Never give generic advice."

---

## Lambda 5 — terraformExport (stretch goal)

File: backend/terraform_export/handler.py
API route: POST /terraform
Only attempt this if core flow is fully working by hour 8.

### Input
{ "sessionId": "uuid-string" }

### What it does
Step 1: Fetch session from DynamoDB. Get generatedConfig and
selectedService. Extract only the value from each field —
ignore the reason, Terraform only needs values.

Step 2: Query MCP via Bedrock for Terraform resource schema.

Step 3: Bedrock generates valid .tf file content.

Step 4: Return the .tf content as a string.

### Output
{ "terraformContent": "resource aws_s3_bucket example {...}" }

---

## API Gateway Routes

POST /intent → extractIntent Lambda
POST /schema → fetchSchema Lambda
POST /config → generateConfig Lambda
POST /explain → explainField Lambda
POST /terraform → terraformExport Lambda (stretch)

All routes must have CORS enabled.
Response headers must include: Access-Control-Allow-Origin: *

---

## Local Flask Server (for development)

Port: 5000
React frontend uses http://localhost:5000 during development.
Switch to API Gateway URL for final deployment.

---

## Error Handling Rules

200 for success. 400 for bad input. 500 for internal errors.

For Bedrock JSON parsing errors — catch and retry once with
a stricter prompt telling it to return only valid JSON.
For DynamoDB errors — log and return 500.
For S3 cache miss — continue to MCP, do not fail.
For MCP timeout — use pre-cached schema if available.
