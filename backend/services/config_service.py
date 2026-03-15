# Config generation service
# 1. Load session from DynamoDB
# 2. Fetch relevant compliance docs from S3
# 3. Build prompt with weights + fields + compliance text
# 4. Call Bedrock — every field gets value + reason
# 5. Save config to DynamoDB
# 6. Return config map
