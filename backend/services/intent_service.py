# Intent extraction service
# 1. Call Bedrock to extract structured profile from description
# 2. Call weights_engine.compute_weights()
# 3. Save session to DynamoDB
# 4. Return sessionId + intent + weights
