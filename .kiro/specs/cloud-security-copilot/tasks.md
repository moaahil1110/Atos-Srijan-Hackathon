# Implementation Plan: Cloud Security Copilot

## Overview

This implementation plan converts the Cloud Security Copilot design into discrete coding tasks. The system consists of five AWS Lambda functions, two pure Python modules (weights_engine.py and field_classifier.py), a React frontend, and supporting AWS infrastructure. The implementation follows a bottom-up approach: core logic first, then Lambda functions, then frontend integration.

The system uses Python for all backend code and React/JavaScript for the frontend. All AI calls use Amazon Bedrock with Claude 3 Sonnet. AWS service schemas are fetched via the AWS Documentation MCP server.

## Tasks

- [ ] 1. Implement core Python modules
  - [~] 1.1 Implement weights_engine.py
    - Create compute_weights function with exact algorithm from design
    - Implement security score calculation with 0.40 floor enforcement
    - Implement compliance score calculation with framework counting
    - Implement cost score calculation with 0.25 ceiling
    - Implement normalization and post-normalization security floor enforcement
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [~] 1.2 Write unit tests for weights_engine.py
    - Test healthcare company profile (high security weight expected)
    - Test e-commerce company profile (higher cost weight expected)
    - Test security floor enforcement (ensure never below 0.40)
    - Test cost ceiling enforcement (ensure never above 0.25)
    - Test weight sum equals 1.0 within tolerance
    - _Requirements: 2.2_
  
  - [~] 1.3 Implement field_classifier.py
    - Create classify_field function
    - Implement effective priority score calculation
    - Implement instruction tag assignment logic (LOCKED_SECURE, PREFER_SECURE, OPTIMISE_COST, BALANCED)
    - Implement compliance boost multiplier for active frameworks
    - _Requirements: 4.1, 4.2, 4.3, 4.4_


  - [~] 1.4 Write unit tests for field_classifier.py
    - Test LOCKED_SECURE tag assignment for critical security fields
    - Test PREFER_SECURE tag assignment for high security fields
    - Test OPTIMISE_COST tag assignment for cost-relevant fields
    - Test compliance boost multiplier application
    - _Requirements: 4.2_

- [ ] 2. Set up AWS infrastructure
  - [~] 2.1 Create DynamoDB table
    - Create CopilotSessions table with sessionId as partition key
    - Configure on-demand billing mode
    - Set region to ap-south-1
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [~] 2.2 Create S3 buckets
    - Create cloud-copilot-schemas bucket for schema cache
    - Create cloud-copilot-compliance-docs bucket for compliance documents
    - Set appropriate bucket policies and CORS configuration
    - _Requirements: 5.1, 5.2_
  
  - [~] 2.3 Upload compliance documents to S3
    - Upload hipaa-access-controls.txt with clause §164.312(a)(1)
    - Upload hipaa-encryption.txt with clause §164.312(e)(2)(ii)
    - Upload hipaa-logging.txt with clause §164.312(b)
    - Upload pcidss-access.txt with Requirement 7
    - Upload pcidss-encryption.txt with Requirements 3 and 4
    - Upload pcidss-logging.txt with Requirement 10
    - Upload soc2-access.txt with CC6.1
    - Upload soc2-logging.txt with CC7.2
    - _Requirements: 5.3, 5.4, 5.5, 6.3_
  
  - [~] 2.4 Configure Amazon Bedrock access
    - Enable Claude 3 Sonnet model access in Bedrock console
    - Verify model ID: anthropic.claude-3-sonnet-20240229-v1:0
    - Configure IAM permissions for Lambda to invoke Bedrock
    - _Requirements: 1.1, 4.1, 6.2_

- [ ] 3. Implement extractIntent Lambda function
  - [~] 3.1 Create Lambda handler for intent extraction
    - Set up Python 3.11 runtime with boto3
    - Implement POST /intent request parsing
    - Validate Company_Description input (non-empty, max 5000 chars)
    - _Requirements: 1.1, 1.5, 11.4_
  
  - [~] 3.2 Implement Bedrock intent extraction
    - Build intent extraction prompt from design document
    - Call Bedrock with Company_Description
    - Parse JSON response with error handling and retry logic
    - Extract industry, complianceFrameworks, complianceMaturity, teamSize, costPressure, riskTolerance, missionCriticalServices, dataClassification, weightReasoning
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 11.1_
  
  - [~] 3.3 Integrate weights_engine.py
    - Import compute_weights function
    - Call compute_weights with extracted intent
    - Validate weights sum to 1.0 within tolerance
    - _Requirements: 2.1, 2.2_
  
  - [~] 3.4 Store session in DynamoDB
    - Generate unique sessionId using uuid4
    - Store companyProfile, computedWeights, conversationHistory (empty array), createdAt
    - Handle DynamoDB errors with appropriate error messages
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 11.3, 11.5_
  
  - [ ] 3.5 Return intent extraction response
    - Format response with sessionId, intent, and weights
    - Ensure response time under 5 seconds
    - _Requirements: 1.1, 12.1_


- [ ] 4. Implement fetchSchema Lambda function
  - [ ] 4.1 Create Lambda handler for schema fetching
    - Set up Python 3.11 runtime with boto3
    - Implement POST /schema request parsing
    - Validate service, provider, and sessionId inputs
    - _Requirements: 3.1, 3.5_
  
  - [ ] 4.2 Implement S3 schema cache check
    - Build cache key: schemas/aws/{service-lowercase}.json
    - Check S3 bucket cloud-copilot-schemas for cached schema
    - Return cached schema immediately if found
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [ ] 4.3 Implement MCP server integration
    - Configure Bedrock to use AWS Documentation MCP server as tool
    - Query MCP for AWS service documentation
    - Handle MCP timeout and connection errors
    - _Requirements: 3.1, 3.2, 3.5, 11.2_
  
  - [ ] 4.4 Implement schema structuring with Bedrock
    - Build schema structuring prompt from design document
    - Call Bedrock with raw MCP documentation
    - Parse JSON response to extract fields with fieldId, label, type, options, required, securityRelevance, costRelevance, complianceRelevance, aiExplainable
    - _Requirements: 3.2, 3.3, 3.4, 9.1, 9.2, 9.3_
  
  - [ ] 4.5 Integrate field_classifier.py
    - Fetch session from DynamoDB to get weights and active frameworks
    - Import classify_field function
    - Call classify_field on each field in schema
    - Add instruction, effectivePriority, and complianceActive to each field
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 7.6_
  
  - [ ] 4.6 Cache classified schema to S3
    - Write classified schema to S3 with cache key
    - Handle S3 write errors gracefully
    - _Requirements: 5.1, 11.3_
  
  - [ ] 4.7 Return schema response
    - Format response with provider, service, and fields array
    - Ensure response time under 10 seconds per service
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 12.3_

- [ ] 5. Checkpoint - Ensure extractIntent and fetchSchema work end-to-end
  - Test with healthcare company description and S3 service
  - Test with e-commerce company description and RDS service
  - Verify weights are computed correctly
  - Verify schemas are cached and retrieved from S3
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement generateConfig Lambda function
  - [ ] 6.1 Create Lambda handler for config generation
    - Set up Python 3.11 runtime with boto3
    - Implement POST /config request parsing
    - Validate sessionId, schema, and service inputs
    - _Requirements: 4.1, 4.5_
  
  - [ ] 6.2 Fetch session data from DynamoDB
    - Retrieve companyProfile and computedWeights by sessionId
    - Handle session not found errors
    - _Requirements: 7.6, 11.1_
  
  - [ ] 6.3 Implement compliance document fetching
    - Map field complianceRelevance and company frameworks to S3 file path
    - Fetch relevant compliance document from S3
    - Handle missing compliance documents gracefully (use empty string)
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 6.2, 6.3_
  
  - [ ] 6.4 Implement config generation with Bedrock
    - Build config generation prompt from design document
    - Include instruction tags, compliance text, company profile, and weights in prompt
    - Call Bedrock with field list and constraints
    - Parse JSON response to extract value and reason for each field
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 6.5 Validate generated configuration
    - Validate all field names against schema from request
    - Validate all field types match schema
    - Validate all field values meet constraints
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_


  - [ ] 6.6 Store configuration in DynamoDB
    - Update session with generatedConfig and selectedService
    - Handle DynamoDB update errors
    - _Requirements: 7.5, 11.3, 11.5_
  
  - [ ] 6.7 Return config generation response
    - Format response with config map (fieldId -> {value, reason})
    - Ensure response time under 15 seconds for up to 10 services
    - _Requirements: 4.1, 4.2, 4.6, 8.1, 12.4_

- [ ] 7. Implement explainField Lambda function
  - [ ] 7.1 Create Lambda handler for follow-up questions
    - Set up Python 3.11 runtime with boto3
    - Implement POST /explain request parsing
    - Validate sessionId, fieldId, fieldLabel, currentValue, inlineReason, and message inputs
    - _Requirements: 6.1, 6.4_
  
  - [ ] 7.2 Fetch full session from DynamoDB
    - Retrieve companyProfile, computedWeights, selectedService, generatedConfig, conversationHistory
    - Handle session not found errors
    - _Requirements: 6.1, 6.5, 7.6_
  
  - [ ] 7.3 Fetch relevant compliance document
    - Map field complianceRelevance and active frameworks to S3 file path
    - Retrieve compliance document from S3
    - Handle missing documents gracefully
    - _Requirements: 6.2, 6.3, 6.6_
  
  - [ ] 7.4 Build conversation context
    - Initialize conversationHistory if empty with synthetic opening using inlineReason
    - Append user message to conversationHistory
    - _Requirements: 6.1, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 7.5 Implement explanation generation with Bedrock
    - Build explanation system prompt from design document
    - Include company context, compliance text, inline reason, and conversation history
    - Call Bedrock with full context
    - Parse response for UPDATE_FIELD signal
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 7.6 Update DynamoDB with conversation and config changes
    - Append AI response to conversationHistory
    - If UPDATE_FIELD present, update generatedConfig with newValue and newReason
    - Handle DynamoDB update errors
    - _Requirements: 7.5, 11.3, 11.5_
  
  - [ ] 7.7 Return explanation response
    - Format response with explanation text and optional configUpdate
    - Ensure response time under 8 seconds
    - _Requirements: 6.1, 6.4, 12.5_

- [ ] 8. Checkpoint - Ensure all Lambda functions work end-to-end
  - Test full flow: extractIntent -> fetchSchema -> generateConfig -> explainField
  - Test healthcare company with HIPAA compliance citations
  - Test e-commerce company with cost optimization
  - Test follow-up questions and config updates
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement API Gateway integration
  - [ ] 9.1 Create API Gateway REST API
    - Create REST API named "CloudSecurityCopilotAPI"
    - Create prod stage
    - Set region to ap-south-1
    - _Requirements: 1.1, 3.1, 4.1, 6.1_
  
  - [ ] 9.2 Create API routes
    - Create POST /intent route pointing to extractIntent Lambda
    - Create POST /schema route pointing to fetchSchema Lambda
    - Create POST /config route pointing to generateConfig Lambda
    - Create POST /explain route pointing to explainField Lambda
    - _Requirements: 1.1, 3.1, 4.1, 6.1_
  
  - [ ] 9.3 Configure CORS
    - Enable CORS on all routes
    - Set Access-Control-Allow-Origin: *
    - Set appropriate allowed methods and headers
    - _Requirements: 11.1_


  - [ ] 9.4 Test API Gateway endpoints
    - Test each endpoint with curl or Postman
    - Verify CORS headers in responses
    - Verify error handling for invalid inputs
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ] 10. Implement React frontend
  - [ ] 10.1 Set up React project structure
    - Initialize React app with create-react-app
    - Create src/App.jsx as main component
    - Create src/IntakePanel.jsx component
    - Create src/ConfigPanel.jsx component
    - Create src/ExplainPanel.jsx component
    - _Requirements: 1.1, 4.1, 6.1_
  
  - [ ] 10.2 Implement IntakePanel component
    - Create company description textarea (max 5000 chars)
    - Create AWS service selector dropdown (S3, RDS, EC2, IAM, Lambda, ElastiCache, CloudFront, ECS)
    - Create submit button
    - Display extracted profile and weights when session exists
    - _Requirements: 1.1, 1.5, 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ] 10.3 Implement ConfigPanel component
    - Group fields by securityRelevance (critical, high, other)
    - Display fieldId, label, value, and inline reason for each field
    - Add "tailored" badge for aiExplainable fields
    - Add "Ask follow-up" button for aiExplainable fields
    - Highlight active field during conversation
    - _Requirements: 4.1, 4.2, 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ] 10.4 Implement ExplainPanel component
    - Display conversation history with user and AI messages
    - Create input area for follow-up questions
    - Implement send button and Enter key handling
    - Show empty state message when no conversation exists
    - _Requirements: 6.1, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 10.5 Implement App.jsx state management
    - Manage session, schema, config, conversation, activeField, loading states
    - Implement handleSubmit to call /intent, /schema, /config in sequence
    - Implement handleFollowUp to call /explain and update config if needed
    - Display loading messages during API calls
    - _Requirements: 1.1, 3.1, 4.1, 6.1, 7.6, 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ] 10.6 Implement API integration
    - Configure API base URL (localhost:5000 for dev, API Gateway URL for prod)
    - Implement fetch calls for all endpoints with error handling
    - Handle config updates from explainField responses
    - Update both value and reason when configUpdate received
    - _Requirements: 1.1, 3.1, 4.1, 6.1, 11.1, 11.2, 11.3, 11.4_
  
  - [ ] 10.7 Implement styling
    - Create three-panel layout (280px left, flexible center, 320px right)
    - Style field groups with color-coded headers (red for critical, amber for high, gray for other)
    - Style inline reasons as italic text always visible
    - Style active field with light blue background
    - Style conversation messages with user/AI differentiation
    - _Requirements: 8.1, 8.5_

- [ ] 11. Checkpoint - Ensure frontend integrates with backend
  - Test full user flow from company description to config generation
  - Test follow-up questions and live config updates
  - Test with multiple company profiles and services
  - Verify inline reasons are always visible
  - Verify compliance citations appear in explanations
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Implement local Flask development server
  - [ ] 12.1 Create backend/app.py Flask server
    - Set up Flask app on port 5000
    - Enable CORS with flask-cors
    - Create routes for /intent, /schema, /config, /explain
    - Import and call Lambda handler functions
    - _Requirements: 1.1, 3.1, 4.1, 6.1_
  
  - [ ] 12.2 Test local development setup
    - Run Flask server on localhost:5000
    - Run React dev server on localhost:3000
    - Verify frontend can call backend locally
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_


- [ ] 13. Deploy to AWS
  - [ ] 13.1 Package and deploy Lambda functions
    - Create deployment packages for each Lambda with dependencies
    - Upload to AWS Lambda in ap-south-1 region
    - Configure memory (512 MB) and timeout (60 seconds)
    - Set environment variables for S3 bucket names and DynamoDB table name
    - _Requirements: 1.1, 3.1, 4.1, 6.1, 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ] 13.2 Deploy frontend to AWS Amplify
    - Initialize Amplify in frontend directory
    - Configure Amplify hosting
    - Update API base URL to API Gateway URL
    - Run amplify publish
    - _Requirements: 1.1, 3.1, 4.1, 6.1_
  
  - [ ] 13.3 Test deployed application
    - Test full flow on deployed URL
    - Verify all API calls work through API Gateway
    - Test error handling and edge cases
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 14. Pre-cache AWS service schemas
  - [ ] 14.1 Generate and upload S3 schema
    - Run fetchSchema for S3 service
    - Verify schema includes BlockPublicAcls, ServerSideEncryptionConfiguration, VersioningConfiguration, LoggingConfiguration, LifecycleConfiguration
    - Upload to S3 at schemas/aws/s3.json
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 10.5_
  
  - [ ] 14.2 Generate and upload RDS schema
    - Run fetchSchema for RDS service
    - Verify schema includes encryption, backup, and access control fields
    - Upload to S3 at schemas/aws/rds.json
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 10.2_
  
  - [ ] 14.3 Generate and upload IAM schema
    - Run fetchSchema for IAM service
    - Verify schema includes MFA, password policy, and access key fields
    - Upload to S3 at schemas/aws/iam.json
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 10.1_

- [ ] 15. Implement demo contrast scenarios
  - [ ] 15.1 Test healthcare company scenario
    - Input: "20-person healthcare startup in Bengaluru storing patient records. Working toward HIPAA compliance. Security is non-negotiable."
    - Verify weights: security ~0.62, compliance ~0.28, cost ~0.10
    - Verify S3 config: BlockPublicAcls true, encryption SSE-KMS, logging true, lifecycle false
    - Verify HIPAA §164.312 citations in explanations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.3, 4.1, 4.2, 4.6, 6.3, 8.2, 8.3_
  
  - [ ] 15.2 Test e-commerce company scenario
    - Input: "Small e-commerce company selling handmade goods. No compliance obligations. AWS bill is our biggest cost."
    - Verify weights: security ~0.50, compliance ~0.00, cost ~0.25
    - Verify S3 config: BlockPublicAcls true, encryption SSE-S3, logging false, lifecycle true
    - Verify cost optimization reasoning in explanations
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.5, 4.1, 4.2, 8.4_
  
  - [ ] 15.3 Test follow-up question flow
    - Ask "Can we use SSE-S3 instead to reduce costs?" on healthcare scenario
    - Verify AI explains why SSE-KMS is maintained for HIPAA
    - Verify AI suggests SSE-S3 for non-PHI buckets as alternative
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.2, 8.3, 8.4_

- [ ] 16. Final checkpoint - End-to-end validation
  - Run both demo scenarios on deployed application
  - Verify all compliance citations are accurate
  - Verify all inline reasons are company-specific
  - Verify config updates work correctly in follow-up questions
  - Verify response times meet requirements (intent <5s, schema <10s, config <15s, explain <8s)
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Stretch goal: Implement terraformExport Lambda function
  - [ ] 17.1 Create Lambda handler for Terraform export
    - Set up Python 3.11 runtime with boto3
    - Implement POST /terraform request parsing
    - Validate sessionId input
    - _Requirements: 13.1, 13.2_
  
  - [ ] 17.2 Implement Terraform generation
    - Fetch session configuration from DynamoDB
    - Query MCP for Terraform resource schema
    - Call Bedrock to generate valid .tf file
    - Preserve inline reasoning as comments in Terraform
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ] 17.3 Add Terraform export to frontend
    - Add "Export to Terraform" button in ConfigPanel
    - Call POST /terraform endpoint
    - Display or download .tf file content
    - _Requirements: 13.1, 13.2, 13.3_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Python is used for all backend Lambda functions and core modules
- React/JavaScript is used for the frontend single-page application
- All AI calls use Amazon Bedrock with Claude 3 Sonnet model
- AWS Documentation MCP server provides real-time AWS service schemas
- Compliance documents in S3 ground all explanations in authoritative standards
- The system maintains conversational context in DynamoDB for coherent multi-turn interactions
