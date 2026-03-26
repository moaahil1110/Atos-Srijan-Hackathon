# Final Sprint Plan - Nimbus

This is the final sprint split for the team of 4. The goal is to finish Nimbus as a cloud optimization and recommendation copilot where:

- The user gives company context plus current cloud field values
- The system uses company context, compliance documentation, and provider documentation before making every decision
- The system returns optimized or recommended field values with clear reasoning
- Terraform generation is always available at the end after the user gets the final field values

## Core Product Direction

Nimbus is not just a recommendation bot. It must behave like a grounded advisor.

For every important decision, the model must refer to:

- The company description provided by the user
- The user's current cloud configuration fields and values
- Compliance documents relevant to that company
- Cloud provider documentation for the relevant provider and service

The output should explain why the selected value is best for:

- That company's context
- That field name and field description
- That provider's supported options
- That compliance standard

Terraform is not a separate early feature. It is a mandatory final output option after recommendation/optimization is complete.

---

## 1. Musharraf - Environment and Credentials Owner

Musharraf is responsible for replacing the old account setup and preparing the full environment credentials for the team.

### What Musharraf must do

He must create or arrange the required cloud resources and then share the correct values needed for the backend `.env`.

### AWS items to create

1. Create or provide one AWS account/project for Nimbus
2. Create an IAM user or IAM role for the app
3. Give programmatic access credentials for backend usage
4. Create a DynamoDB table for sessions
5. Create an S3 bucket for compliance/provider documents or stored knowledge files
6. Ensure Bedrock access is enabled in the selected AWS region
7. If Bedrock Knowledge Base will be used, create or share the Knowledge Base ID
8. Confirm the region that all AWS resources are using

### AWS things he must share

He should share these exact values:

- `AWS_REGION`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN` if temporary credentials are being used
- `DYNAMO_TABLE`
- `S3_BUCKET`
- `BEDROCK_MODEL_ID`
- `BEDROCK_KB_ID` if Bedrock KB is being used
- `BEDROCK_AWS_ACCESS_KEY_ID` if separate Bedrock credentials are used
- `BEDROCK_AWS_SECRET_ACCESS_KEY` if separate Bedrock credentials are used

### AWS resource notes

- DynamoDB table should store app session data
- S3 bucket should store uploaded docs, compliance docs, provider docs, or RAG source docs if AWS is chosen as storage
- Bedrock model access must be enabled for the model Nimbus uses
- Permissions should allow DynamoDB read/write, S3 read/write, and Bedrock invoke access

### Azure items to create or arrange

1. Create or provide an Azure subscription/resource group for Nimbus
2. Set up Azure MCP access for documentation lookup
3. If Azure docs are exposed through a hosted MCP endpoint, create that endpoint
4. If Azure MCP requires auth, generate the auth token

### Azure things he must share

- `AZURE_MCP_COMMAND` if running MCP over stdio
- `AZURE_MCP_ARGS`
- `AZURE_MCP_URL` if using hosted/HTTP MCP
- `AZURE_MCP_AUTH_TOKEN` if required
- Azure subscription name or ID
- Resource group name if relevant to docs or infra access

### GCP items to create or arrange

1. Create or provide a GCP project for Nimbus
2. Set up GCP MCP access for documentation lookup
3. If GCP docs are exposed through a hosted MCP endpoint, create that endpoint
4. If GCP MCP requires auth, generate the auth token

### GCP things he must share

- `GCP_MCP_COMMAND` if running MCP over stdio
- `GCP_MCP_ARGS`
- `GCP_MCP_URL` if using hosted/HTTP MCP
- `GCP_MCP_AUTH_TOKEN` if required
- GCP project ID

### MCP ownership

Musharraf must not forget MCP because provider docs depend on it.

He must verify all 3 provider documentation channels:

- AWS MCP works
- Azure MCP works
- GCP MCP works

For each provider, he should test at least one documentation query and confirm:

- the server starts
- the tool list loads
- documentation text is returned

### What he should finally send you

He should send one clean handoff containing:

1. Full `.env` values for backend
2. Names/IDs of created cloud resources
3. Which credentials are temporary vs permanent
4. Expiry time if temporary credentials are used
5. Any setup steps the backend team must still do locally
6. One short proof that each provider MCP is working

### Simple message for Musharraf

Please prepare the complete environment setup for Nimbus because we are moving off the old AWS account. I need the full backend `.env` credentials and the cloud resources created for AWS, Azure, and GCP. On AWS, create/share the region, access keys, DynamoDB table, S3 bucket, Bedrock model access, and Bedrock KB ID if available. On Azure and GCP, I need the MCP setup details so our backend can fetch provider documentation, including command/args or URL/token depending on how the MCP is exposed. Please send everything in one clean list and confirm each MCP actually returns docs.

---

## 2. Aahil - Compliance and Documentation Owner

Aahil is responsible for collecting the full documentation corpus that Nimbus will use for grounded reasoning.

### What Aahil must do

He must gather the complete documents, not short snippets. The model should be able to refer to the source material in detail.

### Documents he must collect

#### Company context documentation

This includes the types of company material the user may upload or provide:

- Company profile or business description examples
- Security policy documents
- Internal architecture or infrastructure notes
- Data classification policies
- Access control policies
- Encryption standards
- Logging and monitoring standards
- Backup/disaster recovery policies
- Vendor/security review documents if relevant

#### Compliance documentation

He should gather full or near-complete official/reference documentation for the compliance families Nimbus supports or plans to support, such as:

- HIPAA
- PCI-DSS
- SOC 2
- ISO 27001 if we want to extend
- GDPR if company context may require it

For each compliance framework, collect documents related to:

- Access control
- Encryption
- Logging and monitoring
- Identity and authentication
- Network protection
- Data retention
- Backup and recovery
- Audit evidence

#### Cloud provider documentation

He should gather the full service documentation needed for recommendation and optimization across:

- AWS
- Azure
- GCP

For each provider, documents should cover:

- Service overview
- Field/parameter descriptions
- Allowed values or options
- Security best practices
- Compliance guidance
- Limits/constraints
- Pricing/cost tradeoff notes if useful
- Terraform field mapping if available

#### Service-level priority docs

Focus first on the services already represented in the repo schemas:

- AWS: S3, RDS, IAM, EC2, Lambda, CloudFront
- Azure: Blob Storage, PostgreSQL, Virtual Machines, Azure Functions, Azure CDN, Azure Active Directory
- GCP: Cloud Storage, Cloud SQL, Compute Engine, Cloud Functions, Cloud CDN, Cloud IAM

### Format and quality rules

Aahil should make sure the docs are:

- Full documents, not 2-3 copied lines
- Cleanly named
- Split by provider/framework/topic if too large
- Stored in a structured folder layout
- Source-attributed so we know where each document came from
- Usable for ingestion into RAG

### Suggested folder structure for his deliverable

```text
docs-source/
  company-context/
  compliance/
    hipaa/
    pci-dss/
    soc2/
  cloud/
    aws/
      s3/
      rds/
      iam/
    azure/
      blob-storage/
      postgresql/
    gcp/
      cloud-storage/
      cloud-sql/
```

### Metadata he should include with each doc

- Document name
- Provider or compliance family
- Service name if relevant
- Topic such as encryption/access/logging/networking
- Source link
- Version/date if available
- Whether it is official documentation or internal company context

### What he should finally send you

1. The full document collection
2. Clear folder structure
3. Source links list
4. A summary of what is complete and what is still missing
5. A document inventory sheet so Mir can ingest it cleanly

### Simple message for Aahil

Please collect the complete documentation set Nimbus needs so the model can make grounded decisions. I need full docs, not short extracts. Gather company-context style documents, compliance documents like HIPAA/PCI-DSS/SOC 2, and cloud provider docs for AWS/Azure/GCP services and their fields, options, security guidance, and compliance-relevant behavior. Organize everything clearly with source links and metadata so it can be fed into RAG without cleanup.

---

## 3. Mir - RAG and Knowledge Layer Owner

Mir is responsible for building the complete RAG structure so the model can actually use the documents gathered by Aahil.

### What Mir must do

He must design and implement the storage and retrieval pipeline for:

- Compliance docs
- Provider docs
- Company context docs

The aim is that before the model answers, it can retrieve the most relevant material for the current company, field, provider, and service.

### RAG responsibilities

1. Decide where docs are stored
2. Build ingestion pipeline
3. Chunk documents properly
4. Add metadata tags
5. Create retrieval strategy
6. Return the best context for prompts
7. Support filtering by company, compliance framework, provider, service, topic, and field

### Recommended structure

Mir should create a RAG pipeline with these logical layers:

1. Document storage
   - S3 if AWS-based storage is preferred
   - another cloud/vector store only if clearly better and easy to integrate

2. Pre-processing
   - cleaning
   - chunking
   - normalization
   - metadata extraction

3. Indexing
   - embeddings/vector index or Bedrock KB if chosen
   - metadata filters

4. Retrieval
   - query by provider + service + field + compliance + company context
   - top-k context selection
   - source traceability

5. Prompt context packaging
   - compact but strong combined context for the backend

### Metadata Mir should support

Each chunk should ideally include:

- doc_type: `company_context`, `compliance`, `provider_doc`
- provider: `aws`, `azure`, `gcp`
- service
- framework: `hipaa`, `pci-dss`, `soc2`, etc.
- topic: `encryption`, `access`, `logging`, `network`, etc.
- field_name if applicable
- source
- version/date

### Retrieval expectations

For a single backend decision, the retriever should be able to fetch:

- relevant company context
- relevant compliance chunks
- relevant provider/service documentation
- maybe relevant field-level description text

This should be combined so the model can explain:

- why this value fits the company
- why it matches compliance
- why it matches provider documentation

### What Mir should finally deliver

1. Storage design choice and reason
2. Folder/bucket/index structure
3. Ingestion scripts or pipeline
4. Retrieval API or helper contract for backend
5. Metadata schema
6. Example retrieved context for one real query
7. Clear note on latency and scalability tradeoffs

### Simple message for Mir

Please build the full RAG structure for Nimbus so the model can use company docs, compliance docs, and provider docs before making decisions. I need proper ingestion, chunking, metadata, storage, and retrieval, not just raw file storage. The retriever should support filtering by provider, service, field, company context, and compliance framework so the backend can ask for the best combined context before generating recommendations or optimizations.

---

## 4. Your Ownership - Backend, Logic, and UI Changes

You are responsible for the product behavior and the final logic integration.

### Main backend goal

Before the model makes any recommendation, optimization, or explanation, it should check:

1. Company context
2. Existing user field values
3. Relevant compliance documents
4. Relevant cloud provider/service documentation
5. Field name and field description

The model should behave like it has all the reference books before it answers.

### Backend changes to implement

#### A. Ground every decision with combined context

Update the logic so recommendation/optimization prompts include:

- company profile
- current config if provided
- relevant compliance context
- relevant provider docs
- field schema details

This should happen from the thinking stage itself, not only in the final explanation.

#### B. Improve optimize flow

When the user sends:

- company description
- current cloud field values

Nimbus should return optimal values for those fields, grounded in:

- company needs
- provider docs
- compliance docs
- security/cost logic

#### C. Improve recommendation flow

The recommendation feature already exists, but it needs logic upgrades so that field choices are made using the same grounded context approach.

#### D. Make Terraform a mandatory final step

After recommendation or optimization is complete:

- the user should always have the option to generate Terraform
- Terraform should come after field finalization, not as a separate initial feature

#### E. UI updates

Update the frontend so the user flow reflects:

1. Enter company description
2. Enter or review current field values
3. Get grounded recommended/optimized values
4. View reasoning
5. Generate Terraform

### Concrete technical direction based on current repo

From the current codebase, these areas likely need updates:

- backend prompt construction in recommendation/optimization/explanation services
- `kb_client` and related retrieval helpers so compliance + provider docs are both fetched
- MCP-backed provider documentation retrieval flow
- session storage if company docs or extra retrieved context must be persisted
- frontend workspace panels to make Terraform the end action after results

### Suggested final deliverables from you

1. Updated backend prompt and retrieval flow
2. Unified context assembly for company + compliance + provider docs
3. Improved optimize and recommendation logic
4. Terraform shown as the final mandatory option
5. UI polish for the new flow
6. End-to-end demo path ready for sprint close

---

## Sprint Acceptance Criteria

The sprint is complete only if all of this works together:

1. New environment credentials are ready and working
2. Full document corpus is collected
3. RAG can retrieve relevant provider/compliance/company context
4. Backend uses that context before making decisions
5. Recommendation and optimization both use the grounded flow
6. Terraform generation is available after final values are produced
7. Demo can clearly show why a value was chosen using company + compliance + provider reasoning

---

## Immediate Priority Order

1. Musharraf finishes environment and MCP handoff
2. Aahil finishes document collection and inventory
3. Mir wires the full RAG pipeline on top of that corpus
4. You integrate grounded decision-making into backend and UI

---

## Short Team Summary

- Musharraf: environment, accounts, resources, `.env`, MCP connectivity
- Aahil: complete company/compliance/provider documentation corpus
- Mir: complete RAG ingestion, storage, metadata, retrieval
- You: backend logic, prompt grounding, optimization/recommendation flow, Terraform-end flow, UI updates
