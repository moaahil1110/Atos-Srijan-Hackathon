# Explain / counter-ask service
# 1. Load session + conversation history from DynamoDB
# 2. Fetch matching compliance doc from S3
# 3. Seed context with inline reason if first message
# 4. Call Bedrock with full conversation history
# 5. Parse UPDATE_FIELD signal if present
# 6. Save updated history (+ config update) to DynamoDB
# 7. Return response + configUpdate
