# Model Context Protocol (MCP) Server Documentation

## 1. Overview
TransitPulse exposes a hardened, secure, read-only MCP Server adhering to the Anthropic Model Context Protocol specification. This enables LLM agents and AI clients (Claude Desktop, Cursor, Custom Agents) to query transit, schedule, and attendance data with tenant-scoped isolation.

## 2. Core Security Invariants
- **Read-Only Enforced**: No mutation tools exist in the MCP server. All mutations must go through authenticated REST API endpoints.
- **Tenant Scope Isolation**: Every MCP session requires `client_id` and authorized token with explicit scopes. Cross-tenant access is rejected with `SCOPE_DENIED` or `UNAUTHORIZED`.
- **Immutable Audit Logging**: Every tool execution is recorded in `mcp_audit_logs` with redacted parameters, latency, status, and client ID.
- **Parameter Redaction & Safety**: Sensitive tokens and passwords are scrubbed before storage or display.

## 3. Available MCP Tools

### `get_transit_status`
- **Description**: Retrieves live and static status for Mumbai local trains on Western, Central, and Harbour lines.
- **Input**: `line_code` (str, e.g. "WR"), `station_code` (str, e.g. "CCG")
- **Scopes**: `transit:read`

### `get_user_schedule`
- **Description**: Returns today's class or work timetable slots for a member.
- **Input**: `member_id` (UUID), `date` (YYYY-MM-DD)
- **Scopes**: `schedule:read`

### `get_attendance_summary`
- **Description**: Fetches current attendance percentage, present/absent tallies, and risk status.
- **Input**: `member_id` (UUID)
- **Scopes**: `attendance:read`

### `check_commute_intelligence`
- **Description**: Computes deterministic commute recommendations, optimal departure time, and late-arrival probability based on current train delays and timetable slots.
- **Input**: `member_id` (UUID), `target_arrival_time` (HH:MM)
- **Scopes**: `intelligence:read`
