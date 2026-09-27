# Incident Runbook: API Unavailable (HTTP 5xx Spike / Unreachable)

## Symptoms
* `/health` probe failing or timing out.
* Alert `API_HIGH_5XX_RATE` triggered ($\ge 2\%$ 5xx over 5 minutes).

## Diagnosis
1. Check process status:
   ```bash
   systemctl status transitpulse-api || docker ps | grep transitpulse
   ```
2. Inspect latest structured error logs:
   ```bash
   journalctl -u transitpulse-api --since "10 min ago" | grep '"level": "ERROR"'
   ```
3. Check CPU/Memory exhaustion:
   ```bash
   htop || free -m
   ```

## Immediate Mitigation
1. Restart unresponsive workers:
   ```bash
   systemctl restart transitpulse-api
   ```
2. If traffic spike caused pool exhaustion, scale container instances behind load balancer.
3. Verify recovery via `/health` and `/ready` endpoints.
