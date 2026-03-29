# Tech Stack & Infrastructure — Cloud Security Copilot

## AWS Region

Primary region: ap-south-1 (Asia Pacific — Mumbai)
Fallback region: ap-southeast-1 (Singapore)
Every team member must use the same region.
Every boto3 client must specify this region explicitly.
Every AWS Console action must be done in this region.

---

## AWS Services — Complete Reference

### Amazon Bedrock
Purpose: All AI/GenAI calls — intent extraction, schema
structuring from MCP docs, config generation, explanations,
counter-asking.
Model ID: anthropic.claude-3-sonnet-20240229-v1:0
Access: Must be enabled in Bedrock → Model Access before use.
Cost: Approximately $0.003 per 1000 input tokens,
      $0.015 per 1000 output tokens.
      Entire hackathon usage estimated $2-5 total.
boto3 client name: bedrock-runtime
How to call: bedrock.invoke_model(modelId=..., body=...)

### AWS Lambda
Purpose: Five serverless functions — all backend logic runs here.
Runtime: Python 3.11
Functions:
  extractIntent — intent extraction + weight computation
  fetchSchema — MCP query + schema structuring + classification
  generateConfig — config value generation
  explainField — Why? explanations + counter-asking
  terraformExport — Terraform file generation (stretch goal)
Memory: 512 MB per function (sufficient for Bedrock calls)
Timeout: 60 seconds (Bedrock calls can take 10-20 seconds)
Deployment: zip file upload via AWS Console or AWS CLI
boto3 client name: lambda

### Amazon API Gateway
Purpose: HTTPS entry point for all frontend calls.
Type: REST API
Stage name: prod
Routes:
  POST /intent → extractIntent Lambda
  POST /schema → fetchSchema Lambda
  POST /config → generateConfig Lambda
  POST /explain → explainField Lambda
  POST /terraform → terraformExport Lambda (stretch)
CORS: Must be enabled on every route.
Response header required: Access-Control-Allow-Origin: *
Base URL format: https://{id}.execute-api.{region}.amazonaws.com/prod

### Amazon DynamoDB
Purpose: Session storage — company profiles, weights, configs,
conversation history.
Table name: CopilotSessions
Partition key: sessionId (String type)
Billing mode: On-Demand (no capacity planning needed)
boto3 resource name: dynamodb
Table operations used:
  put_item — save new session
  get_item — fetch session by sessionId
  update_item — add config or conversation history to session

### Amazon S3
Purpose: Two separate uses — schema cache and compliance docs.

Bucket 1 — Schema cache:
  Name: cloud-copilot-schemas
  Folder structure: schemas/aws/{service-lowercase}.json
  Examples:
    schemas/aws/s3.json
    schemas/aws/rds.json
    schemas/aws/iam.json

Bucket 2 — Compliance documents:
  Name: cloud-copilot-compliance-docs
  Folder structure: compliance/{name}.txt
  Files that must exist before demo:
    compliance/hipaa-access-controls.txt
    compliance/hipaa-encryption.txt
    compliance/hipaa-logging.txt
    compliance/pcidss-access.txt
    compliance/pcidss-encryption.txt
    compliance/pcidss-logging.txt
    compliance/soc2-access.txt
    compliance/soc2-logging.txt

boto3 client name: s3
Operations used:
  get_object — read file from bucket
  put_object — write file to bucket

### AWS Docs MCP Server
Purpose: Real-time AWS service documentation fetching.
Called from: fetchSchema Lambda only.
How it integrates: Bedrock uses it as a tool during invoke_model.
MCP server identifier: awslabs.aws-documentation-mcp-server
Configuration in Kiro mcp.json:
{
  "aws-documentation": {
    "command": "uvx",
    "args": ["awslabs.aws-documentation-mcp-server@latest"],
    "env": { "FASTMCP_LOG_LEVEL": "ERROR" },
    "disabled": false,
    "autoApprove": []
  }
}

### AWS Amplify
Purpose: Frontend hosting and deployment.
What it hosts: The React single-page application.
Deploy command: amplify publish (run from frontend folder)
Output: A public HTTPS URL for the live application.
Connected to: API Gateway URL (set in App.jsx API constant)

### Kiro IDE
Purpose: Spec-driven code generation.
Download: kiro.dev/downloads
Spec file location: .kiro/specs/ (Kiro manages this folder)
Reference docs location: docs/ (team-written, not Kiro's)
How to use: Open agent chat → say "generate {Lambda name}
  according to docs/02_backend.md" → Kiro generates skeleton
  → Person 1 fills in actual logic.
One person (Person 4) operates Kiro and pushes output to GitHub.

---

## IAM Credentials

One AWS account for the entire team.
One IAM user: hackathon-dev with AdministratorAccess policy.
Credentials shared with Person 1 only via private message.
All team members configure AWS CLI with these credentials.

AWS CLI configuration:
  aws configure
  AWS Access Key ID: (from Person 2)
  AWS Secret Access Key: (from Person 2)
  Default region name: ap-south-1
  Default output format: json

Verify connection:
  aws s3 ls                   → should list both buckets
  aws dynamodb list-tables    → should show CopilotSessions

---

## Python Dependencies

Install on every team member's laptop who runs backend code:
  pip install boto3
  pip install flask
  pip install flask-cors

boto3 version: latest (3.x)
flask version: latest (3.x)
flask-cors version: latest

---

## Node/React Dependencies

Install in the frontend folder:
  npx create-react-app .   (initialises the project)
  npm install -g @aws-amplify/cli   (for deployment)

React version: 18.x (installed by create-react-app)
No additional npm packages needed — inline styles only,
no CSS libraries, no component libraries.

---

## Local Development Setup

Backend (Flask server on port 5000):
  cd backend
  python app.py
  Server runs at http://localhost:5000

Frontend (React dev server on port 3000):
  cd frontend
  npm start
  Opens at http://localhost:3000

API constant in App.jsx during development:
  const API = "http://localhost:5000"

API constant in App.jsx for production:
  const API = "https://{your-api-gateway-id}.execute-api.ap-south-1.amazonaws.com/prod"

---

## Compliance Documents — Content Requirements

Each file must contain:
- The clause number visible near the top of the file
- 2-3 paragraphs of the actual clause text
- Plain text format (.txt)

Sources to use:
- HIPAA: HHS.gov → HIPAA Security Rule → 45 CFR Part 164
- PCI-DSS: PCI Security Standards Council → v4.0 quick reference
- SOC2: AICPA Trust Service Criteria document

Clause numbers that must appear in each file:
  hipaa-access-controls.txt → §164.312(a)(1)
  hipaa-encryption.txt → §164.312(e)(2)(ii)
  hipaa-logging.txt → §164.312(b)
  pcidss-access.txt → Requirement 7
  pcidss-encryption.txt → Requirements 3 and 4
  pcidss-logging.txt → Requirement 10
  soc2-access.txt → CC6.1
  soc2-logging.txt → CC7.2

---

## Pre-cached Schema Files

Three schema files must be in S3 before the demo.
These guarantee the demo works even if MCP is slow.

Upload command:
  aws s3 cp schemas/ s3://cloud-copilot-schemas/schemas/ --recursive

File format matches the fetchSchema Lambda output exactly.
Each file includes fieldId, label, type, options,
securityRelevance, costRelevance, complianceRelevance,
aiExplainable, instruction, effectivePriority, complianceActive.

---

## GitHub Repository Structure

cloud-security-copilot/
  .kiro/
    specs/              (Kiro writes here — do not add files)
  docs/
    01_business_logic.md
    02_backend.md
    03_frontend.md
    04_tech_stack.md    (this file)
  backend/
    weights_engine.py
    field_classifier.py
    app.py              (Flask local server)
    extract_intent/
      handler.py
    fetch_schema/
      handler.py
    generate_config/
      handler.py
    explain_field/
      handler.py
    terraform_export/
      handler.py        (stretch goal)
  frontend/
    src/
      App.jsx
      IntakePanel.jsx
      ConfigPanel.jsx
      ExplainPanel.jsx
    package.json
  compliance-docs/      (local copies of uploaded docs)
  README.md

---

## Team Roles Summary

Person 1 — Backend Lead:
  Owns all Lambda functions and Flask server.
  Writes actual Bedrock prompts and DynamoDB logic.
  Pulls Kiro-generated skeletons from GitHub and fills them.
  Shares API Gateway URL with Person 3 at hour 6.

Person 2 — Infrastructure:
  Owns AWS account, all resources, and credentials.
  Tests every Lambda with curl as Person 1 completes them.
  Manages S3 content and DynamoDB data.
  Monitors for AWS errors during the hackathon.

Person 3 — Frontend Lead:
  Owns React app completely.
  Builds against mock data until hour 6.
  Wires real API calls in hour 6.
  Deploys to Amplify in hour 9.

Person 4 — Kiro Operator and Demo Lead:
  Operates Kiro on one laptop — only source of generated code.
  Generates Lambda skeletons and React component shells.
  Pushes all generated code to GitHub for team to pull.
  Owns README, demo video, and submission materials.
  Practises demo script until it takes exactly 90 seconds.

---

## Hour by Hour Plan

Hour 1:
  Person 1: extractIntent Lambda
  Person 2: verify all AWS resources exist and work
  Person 3: ConfigPanel with mock data
  Person 4: generate Lambda skeletons in Kiro

Hour 2:
  Person 1: finish and test extractIntent end-to-end with curl
  Person 2: test extractIntent with curl, report results
  Person 3: ExplainPanel with mock conversation
  Person 4: generate fetchSchema skeleton

Hour 3:
  Person 1: fetchSchema Lambda with MCP integration
  Person 2: verify S3 schema cache is being written
  Person 3: IntakePanel with form and service selector
  Person 4: generate generateConfig skeleton

Hour 4:
  Person 1: generateConfig Lambda
  Person 2: test healthcare vs e-commerce contrast
  Person 3: wire App.jsx with mock data, full flow working
  Person 4: generate explainField skeleton

Hour 5:
  Person 1: explainField Lambda with compliance doc fetch
  Person 2: verify compliance docs are being fetched from S3
  Person 3: polish all three panels, loading states working
  Person 4: generate Flask app.py for local server

Hour 6 — Integration (all four together):
  Person 1 shares API Gateway URL
  Person 3 replaces mock data with real fetch calls
  Person 2 and 4 run full demo flow and report all bugs

Hour 7:
  Person 1: fix backend bugs from integration
  Person 3: fix frontend bugs from integration
  Person 2: run demo flow 10 times, log every issue
  Person 4: start README and architecture diagram

Hour 8:
  Person 1: attempt terraformExport if core is stable
  Person 3: deploy to Amplify, get live URL
  Person 2: final end-to-end test on deployed URL
  Person 4: record 3-minute demo video

Hour 9 — Submission:
  All four: commit everything to GitHub including .kiro/specs/
  Person 4: submit GitHub URL, live URL, demo video
  All four: practice the 90-second live demo pitch

---

## Demo Script — 90 Seconds

30 seconds — Setup:
"Most cloud security tools give everyone the same advice.
A healthcare company and a gaming startup get identical
recommendations. We built something different."

60 seconds — Live demo:
1. Type healthcare company description. Click submit.
2. Wait for config to appear. Point out SSE-KMS encryption,
   logging true, lifecycle false.
3. Click Why? on ServerSideEncryptionConfiguration.
4. Read the HIPAA §164.312 citation aloud.
5. Type counter-ask: "Can we use SSE-S3 instead to reduce costs?"
6. Show AI response explaining why SSE-KMS is maintained for
   HIPAA but SSE-S3 would be acceptable for non-PHI buckets.

30 seconds — Architecture:
"The weights are computed in Python — not a prompt — so security
is guaranteed mathematically. Bedrock uses real AWS field names
fetched live from the AWS Documentation MCP server."
