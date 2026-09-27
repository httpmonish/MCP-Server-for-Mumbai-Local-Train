# Incident Runbook: Model Context Protocol (MCP) Server Failures

## Symptoms
* Metric `mcp_tool_errors_total` spikes.
* AI host receives `500 Internal Server Error` on `/mcp` tool execution endpoints.

## Diagnosis
1. Verify MCP authentication token validity and scopes (`mcp:read`).
2. Test tool discovery directly:
   ```bash
   curl -i http://localhost:8000/mcp/tools
   ```
3. Test tool invocation with valid bearer token:
   ```bash
   curl -X POST http://localhost:8000/mcp/tools/get_my_schedule \
     -H "Authorization: Bearer $VALID_JWT" \
     -H "Content-Type: application/json" \
     -d '{}'
   ```

## Immediate Mitigation
1. If token expired or issuer mismatch, verify client uses `settings.MCP_AUTH_ISSUER` and `MCP_AUTH_AUDIENCE`.
2. Verify underlying database and schedule engine are healthy.
