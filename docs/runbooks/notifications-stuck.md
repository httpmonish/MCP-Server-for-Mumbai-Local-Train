# Incident Runbook: Notification Engine Stuck / Queue Backlog

## Symptoms
* Outbox events remaining in `PENDING` status for $> 2$ minutes.
* Metric `notification_retries_total` or `notification_suppressed_total` elevated.

## Diagnosis
1. Check count of pending Outbox events and stalled notifications:
   ```sql
   SELECT status, count(*) FROM outbox_events GROUP BY status;
   SELECT status, count(*) FROM notifications GROUP BY status;
   ```
2. Inspect worker logs for SendGrid / SMTP provider rate-limiting (429) or timeouts:
   ```bash
   journalctl -u tp-notification-worker | grep 'error_code'
   ```

## Immediate Mitigation
1. If worker process is crashed, restart `tp-notification-worker`.
2. If provider 429 rate limit exceeded, worker will automatically back off using exponential jitter; verify `scheduled_for` timestamps.
3. If provider credentials failed (401), update `NOTIFICATION_SENDGRID_API_KEY` and restart worker.
