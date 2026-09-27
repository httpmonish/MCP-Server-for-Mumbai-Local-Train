# Incident Runbook: Secret or Credential Compromise

## Immediate Containment (SEV1)
1. **Identify the compromised key**:
   * `JWT_SECRET_KEY`
   * `DATABASE_URL` / DB password
   * `REDIS_URL`
   * `NOTIFICATION_SENDGRID_API_KEY`
   * `RAILRADAR_API_KEY`
   * `ENCRYPTION_MASTER_KEY`

2. **Revocation & Key Rotation**:
   * **If `JWT_SECRET_KEY` is compromised**:
     1. Generate new 64-character secret: `openssl rand -hex 32`.
     2. Update `JWT_SECRET_KEY` in environment secrets / Vault.
     3. Flush all active Redis refresh sessions: `redis-cli flushdb`.
     4. Restart API instances. All active user sessions are immediately invalidated and forced to re-login.
   * **If `DATABASE_URL` is compromised**:
     1. Rotate password in PostgreSQL: `ALTER USER postgres WITH PASSWORD 'new_secure_pwd';`
     2. Update connection string in application environment and restart.
   * **If Provider Key (SendGrid / RailRadar) is compromised**:
     1. Revoke the key in the provider console immediately.
     2. Generate a fresh API key and update the deployment secrets.

3. **Audit & Forensics**:
   * Query structured JSON logs for suspicious access patterns during the exposure window using `request_id`, `user_id`, and `org_id`.
