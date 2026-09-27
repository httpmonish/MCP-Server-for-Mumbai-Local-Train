# TransitPulse Disaster Recovery & Business Continuity

## 1. Objectives & Metrics
- **Recovery Point Objective (RPO)**: $< 15$ minutes (Achieved via Continuous PostgreSQL WAL archiving).
- **Recovery Time Objective (RTO)**: $< 30$ minutes (Achieved via automated Docker deployment and database restore automation).

## 2. Recovery Scenarios
1. **Total PostgreSQL Loss**: Restore from latest snapshot + replay WAL logs. Verify table counts and tenant integrity.
2. **Redis Loss**: Non-critical cache degrades gracefully to PostgreSQL static schedules; session tokens fail closed safely.
3. **Transit Provider Outage**: Circuit breaker activates static timetable fallback automatically.

For complete drill procedures and verification commands, see [docs/disaster-recovery.md](docs/disaster-recovery.md).
