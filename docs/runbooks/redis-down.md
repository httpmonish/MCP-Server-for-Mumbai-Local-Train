# Incident Runbook: Redis Cache & Session Store Unavailable

## Symptoms
* `/ready` returns HTTP 503 with `"redis": "disconnected"`.
* Cache misses spike; refresh token operations fail with connection error.

## Degradation Behavior
* Timetable queries gracefully degrade to static timetable database.
* User access token validation continues functioning (stateless JWT).
* Token refresh requests will fail until Redis reconnects.

## Immediate Mitigation
1. Check Redis service status:
   ```bash
   redis-cli -h $REDIS_HOST ping
   ```
2. Check memory usage and eviction status:
   ```bash
   redis-cli info memory
   ```
3. Restart Redis service:
   ```bash
   systemctl restart redis-server || docker restart tp-redis
   ```
