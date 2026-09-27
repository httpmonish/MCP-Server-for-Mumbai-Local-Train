# Incident Runbook: PostgreSQL Database Unavailable

## Symptoms
* `/ready` endpoint returns HTTP 503 with `"database": "error: ..."`
* Metric `db_errors_total` increases rapidly.

## Diagnosis
1. Verify PostgreSQL service status:
   ```bash
   pg_isready -h $DB_HOST -p 5432
   ```
2. Check database connection pool limits:
   ```sql
   SELECT count(*) FROM pg_stat_activity WHERE datname = 'mcp_production';
   ```
3. Check disk space on database server:
   ```bash
   df -h /var/lib/postgresql/data
   ```

## Immediate Mitigation
1. If max connections reached, terminate idle/stuck connections or increase `max_connections`.
2. If disk is full, purge old vacuum logs or expand volume.
3. If PostgreSQL server crashed, restart service:
   ```bash
   systemctl restart postgresql
   ```
4. Verify `/ready` returns HTTP 200.
