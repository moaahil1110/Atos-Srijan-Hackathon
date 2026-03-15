# Schema fetch service
# 1. Check S3 cache for schemas/aws/{service}.json
# 2. If miss: fetch via MCP server
# 3. Run field_classifier on every field
# 4. Cache result to S3
# 5. Return classified schema
