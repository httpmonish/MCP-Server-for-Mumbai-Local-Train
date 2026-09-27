# TransitPulse Master Operations Runbook

This master runbook indexes operational procedures for diagnosing and mitigating production incidents across all TransitPulse components.

## Incident Severity Definitions
- **SEV1 (Critical)**: Primary API outage, database down, or active data breach/leak. Response time: $< 5$ minutes.
- **SEV2 (Major)**: Partial subsystem outage (e.g. live transit provider failure, notification worker halted). Response time: $< 15$ minutes.
- **SEV3 (Minor)**: Degraded non-critical endpoint, cache miss elevation, or minor UI issue. Response time: $< 60$ minutes.

## Runbook Index
1. **[API Down / Unresponsive](docs/runbooks/api-down.md)**: Handling 502/503/504 errors, container crashes, and worker thread exhaustion.
2. **[PostgreSQL Down / Connection Exhaustion](docs/runbooks/database-down.md)**: Mitigating database failovers, connection spikes, and deadlocks.
3. **[Redis Cache Down](docs/runbooks/redis-down.md)**: Managing Redis eviction, connection dropouts, and fallback to static transit data.
4. **[Transit Provider Outage / Degraded](docs/runbooks/transit-provider-down.md)**: Upstream 429/500 errors from RailRadar / m-Indicator, activating static fallback.
5. **[Notifications Stuck / Backlogged](docs/runbooks/notifications-stuck.md)**: Outbox queue backlog, provider rate-limits, and worker recovery.
6. **[MCP Server Down / Scope Denials](docs/runbooks/mcp-down.md)**: AI Agent tool call timeouts and scope authorization errors.
7. **[Database Migration Failure](docs/runbooks/migration-failure.md)**: Rolling back failed migrations safely without data loss.
8. **[Secret / Credential Compromise](docs/runbooks/secret-compromise.md)**: Emergency key rotation (JWT, DB, Provider API keys) and token revocation.
