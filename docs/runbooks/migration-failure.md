# Incident Runbook: Database Migration Failure

## Symptoms
* Application startup fails with `SchemaValidationError` or `UndefinedTable` / `UndefinedColumn`.
* CI migration validation step fails.

## Diagnosis
1. Inspect migration logs for syntax or constraint conflicts:
   ```bash
   alembic current
   alembic history --verbose
   ```
2. Verify table existence in PostgreSQL:
   ```sql
   \dt
   \d notifications
   ```

## Immediate Mitigation & Rollback
1. Never drop populated columns or tables in production without an expand-and-contract transition.
2. If a migration broke production, rollback to the previous migration revision:
   ```bash
   alembic downgrade -1
   ```
3. Restart application workers.
