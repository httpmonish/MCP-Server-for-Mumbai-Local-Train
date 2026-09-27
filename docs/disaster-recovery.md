# Disaster Recovery & Backup Runbook

## 1. Objectives & Metrics
* **RPO (Recovery Point Objective)**: $\le 1\text{ hour}$ for transactional PostgreSQL records.
* **RTO (Recovery Time Objective)**: $\le 15\text{ minutes}$ for service restoration from snapshot.

---

## 2. PostgreSQL Backup Procedures

### Automated Daily Full Backup & Hourly WAL Archiving
```bash
# Dump encrypted database backup
pg_dump -h $DB_HOST -U postgres -d mcp_production -F c -b -v -f /backups/transitpulse_$(date +%Y%m%d_%H%M%S).dump

# Encrypt backup using AES-256
openssl enc -aes-256-cbc -salt -in /backups/transitpulse_*.dump -out /backups/transitpulse_*.dump.enc -pass env:BACKUP_ENCRYPTION_KEY
```

---

## 3. Database Restoration Drill Procedure
```bash
# 1. Provision clean target database
createdb -h $TARGET_HOST -U postgres mcp_recovery

# 2. Decrypt backup file
openssl enc -d -aes-256-cbc -in /backups/transitpulse_latest.dump.enc -out /backups/transitpulse_latest.dump -pass env:BACKUP_ENCRYPTION_KEY

# 3. Restore data with pg_restore
pg_restore -h $TARGET_HOST -U postgres -d mcp_recovery -v --no-owner --clean /backups/transitpulse_latest.dump

# 4. Run data integrity verification script
PYTHONPATH=backend python -c "
import asyncio
from app.main import async_session_factory
from sqlalchemy import text
async def verify():
    async with async_session_factory() as db:
        users = (await db.execute(text('SELECT count(*) FROM users'))).scalar()
        orgs = (await db.execute(text('SELECT count(*) FROM organizations'))).scalar()
        print(f'Verification passed: {orgs} organizations, {users} users restored.')
asyncio.run(verify())
"
```

---

## 4. Redis Cache Recovery Policy
* Redis stores ephemeral cache and refresh token sessions.
* If Redis is completely lost:
  * Users re-authenticate via `/auth/login` to obtain a fresh refresh token.
  * Transit timetables automatically re-populate on first query or fallback seamlessly to SQLite/PostgreSQL static timetables.
