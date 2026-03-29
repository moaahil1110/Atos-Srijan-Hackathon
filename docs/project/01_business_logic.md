# Business Logic — Cloud Security Copilot

## What This Product Does

This is a GenAI-powered cloud configuration advisor. The user
describes their company in plain English. The system reads that
description, understands what the company cares about, and produces
a tailored AWS service configuration — with real AWS field names,
AI-recommended values, and a specific explanation for every
important setting.

Unlike general cloud security tools that give everyone the same
advice, this system adapts every recommendation to the specific
company. A healthcare company working toward HIPAA gets different
settings than a small e-commerce startup with tight cost
constraints — even for the same AWS service.

The system is AWS-only for tomorrow's hackathon. The architecture
is cloud-agnostic by design — the same logic works for Azure and
GCP in the March 27th version by swapping the MCP server and
output field names.

---

## The Core Innovation — Intent-Aware Configuration

Most cloud tools scan infrastructure and report problems. This
system does the opposite — it asks who you are before it touches
any configuration. The company's identity shapes every
recommendation before any AI call is made.

The three things it captures from the company description:
- What industry they are in and what compliance they follow
- How much risk they can tolerate
- How much cost pressure they are under

These three inputs produce three weighted numbers that control
every downstream decision.

---

## Priority Hierarchy — Never Negotiable

Security always comes first. Compliance comes second. Cost comes
last. This hierarchy is enforced mathematically in Python code —
not in a prompt — so it cannot be broken by any user input or
any LLM output.

The rule in plain terms:
- Security is never relaxed to save money
- Compliance requirements are never skipped to cut costs
- Cost optimisation only happens after security and compliance
  are fully satisfied

---

## The Weight Engine — How Priority Becomes Numbers

The weight engine is a Python function that takes the company
profile and returns three numbers summing to 1.0. It is pure
arithmetic — no AI involved. Same input always produces the
same output. This is intentional — the LLM extracts meaning
from prose, but the priority decision is deterministic.

### Security weight rules
- Base value: 0.40 (this is the floor — never goes below this)
- Each point below 3 on risk tolerance adds 0.04
  (risk tolerance 1 = adds 0.08, risk tolerance 2 = adds 0.04)
- Highly confidential data classification adds 0.08
- Maximum security weight: 0.70

### Compliance weight rules
- Base value: 0.00 if no frameworks active
- If any compliance framework is active: base becomes 0.15
- Each additional framework adds 0.05
- Maturity modifier:
  - in-progress adds 0.10 (most vulnerable stage)
  - not-started adds 0.05
  - achieved adds 0.00 (already compliant)

### Cost weight rules
- Formula: (costPressure divided by 5) multiplied by 0.25
- Maximum cost weight: 0.25 (this is the ceiling — never goes above)
- costPressure of 5 gives cost weight of 0.25
- costPressure of 1 gives cost weight of 0.05

### Normalisation
After computing all three raw scores, divide each by their sum
so they total exactly 1.0.

### Final enforcement after normalisation
If security dropped below 0.40 after normalisation:
- Force security to 0.40
- Take the deficit from cost weight first
- If cost weight cannot cover it, take from compliance weight

### Example outputs
Healthcare company — HIPAA in-progress, risk tolerance 1,
cost pressure 2:
- Security: 0.62, Compliance: 0.28, Cost: 0.10

E-commerce company — no compliance, risk tolerance 4,
cost pressure 5:
- Security: 0.50, Compliance: 0.00, Cost: 0.25 (at ceiling)

---

## Field Priority Classification

After the weight engine runs, every field in the service schema
gets tagged with an instruction. This tag tells Bedrock exactly
how much discretion it has on that field. The classifier runs
in Python — not in a prompt.

### The four instruction tags

LOCKED_SECURE
- Applied when: securityRelevance is critical
- What it means: Bedrock must set this to the most secure
  possible value. No exceptions. No cost trade-offs allowed.
- Example fields: BlockPublicAcls, MFADelete, RootAccountMFA

PREFER_SECURE
- Applied when: securityRelevance is high AND security weight
  is above 0.50
- What it means: Bedrock strongly prefers the secure value.
  Can acknowledge a trade-off but should still recommend secure.
- Example fields: VersioningConfiguration, LoggingConfiguration

OPTIMISE_COST
- Applied when: costRelevance is high AND securityRelevance is
  none AND cost weight is above 0.15
- What it means: Bedrock may choose the cost-efficient option.
  Security has already been handled by other fields.
- Example fields: LifecycleConfiguration, StorageClass,
  ReplicationConfiguration

BALANCED
- Applied to all other fields
- What it means: Bedrock uses judgement based on the full
  company profile.

### Compliance boost in classification
If a field's complianceRelevance array contains any framework
that the company has active, that field's effective priority
score is multiplied by 1.6 if maturity is in-progress, or
1.4 if not-started. This means compliance-relevant fields
rank higher and get stricter treatment.

---

## RAG — Compliance Grounding

When a user clicks Why? on any field, the explanation must cite
the actual compliance clause that justifies the recommendation.
This is what makes explanations credible rather than generic.

### How it works
The explainField Lambda checks two things:
1. The field's complianceRelevance tags (set during schema fetch)
2. The company's active compliance frameworks (from DynamoDB session)

It finds the overlap — for example, a healthcare company asking
about an encryption field that has HIPAA in its complianceRelevance.

It then fetches the matching text file from S3:
- HIPAA + encryption → compliance/hipaa-encryption.txt
- HIPAA + access control → compliance/hipaa-access-controls.txt
- HIPAA + logging → compliance/hipaa-logging.txt
- PCI-DSS + access → compliance/pcidss-access.txt
- PCI-DSS + encryption → compliance/pcidss-encryption.txt
- PCI-DSS + logging → compliance/pcidss-logging.txt
- SOC2 + access → compliance/soc2-access.txt
- SOC2 + logging → compliance/soc2-logging.txt

That file's text is injected directly into the Bedrock prompt.
Bedrock reads the actual clause and cites it in the explanation.

### What a good explanation looks like
Without RAG: "Encryption is important for healthcare companies
because patient data is sensitive."

With RAG: "Under HIPAA Security Rule §164.312(e)(2)(ii),
encryption of electronic protected health information during
transmission is an addressable implementation specification.
Given your risk tolerance of 1/5, treating it as required is
the appropriate and defensible choice for your organisation."

---

## Cross-Questioning — Conversational Config

The user can push back on any recommendation. The system
responds with awareness of everything said before in this
session. This is the most important interactive feature.

### How conversation history works
Every message — both user and AI — is saved to DynamoDB in
the conversationHistory array for that session. When the user
sends a new message, the Lambda fetches the full history,
appends the new message, and sends the entire thread to Bedrock.
Bedrock sees every previous exchange and responds in context.

### Two types of pushback

Valid business reason (system may update the config):
User says "we need public access for our marketing images."
AI responds: "For marketing assets that don't contain patient
data, create a separate public bucket. This bucket storing
patient records must stay private. Here's the naming
convention to keep them clear."
AI signals: UPDATE_FIELD with a different field or null.

Invalid pushback on LOCKED_SECURE field:
User says "can we disable encryption to reduce costs?"
AI responds: "This field is locked because your encryption
setting directly falls under HIPAA §164.312(e)(2)(ii). This
cannot be changed regardless of cost pressure. However,
switching from SSE-KMS to SSE-S3 reduces key management costs
while maintaining HIPAA compliance — would you like that
adjustment instead?"

### The UPDATE_FIELD signal
If Bedrock decides a field value should change based on user
input, it ends its response with:
UPDATE_FIELD: {"fieldId": "...", "newValue": "...",
"reason": "..."}
The Lambda parses this, updates DynamoDB, and the frontend
updates the field value live without a page reload.

---

## The Demo Contrast Moment

This is the most important 90 seconds of the presentation.
Run two back-to-back configurations for S3.

Company A — healthcare:
Description: "20-person healthcare startup in Bengaluru storing
patient records. Working toward HIPAA compliance. Security is
non-negotiable."
Expected weights: security 0.62, compliance 0.28, cost 0.10
Expected config: BlockPublicAcls true, encryption SSE-KMS,
logging true, lifecycle false.

Company B — e-commerce:
Description: "Small e-commerce company selling handmade goods.
No compliance obligations. AWS bill is our biggest cost."
Expected weights: security 0.50, compliance 0.00, cost 0.25
Expected config: BlockPublicAcls true (still — security floor),
encryption SSE-S3 (cheaper), logging false, lifecycle true
(cost saving).

Then click Why? on the encryption field for Company A.
The explanation should cite §164.312(e)(2)(ii) specifically.
That citation wins the demo.

---

## AWS Services Supported Tomorrow

S3 — Simple Storage Service (primary demo service)
RDS — Relational Database Service
IAM — Identity and Access Management
EC2 — Elastic Compute Cloud
Lambda — Serverless Functions
ElastiCache — Caching Service
CloudFront — Content Delivery Network
ECS — Elastic Container Service

For any service not pre-cached in S3, the MCP server fetches
the field names dynamically. Pre-cached schemas exist for S3,
RDS, and IAM as demo insurance.

---

## What We Are NOT Building Tomorrow

- Azure or GCP support (architecture supports it, not today)
- Existing config optimiser (March 27th)
- Full Bedrock Knowledge Base with vector search (March 27th)
- CloudFormation or ARM template export (March 27th)
- Trade-off simulation across multiple services (March 27th)
- Multi-session persistent history (March 27th)
- Terraform export — attempt only if core is fully working by hour 8
