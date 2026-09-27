# Incident Runbook: Live Transit Provider Outage / Degradation

## Symptoms
* Metric `transit_provider_errors_total` spikes.
* `transit_data_freshness_seconds` exceeds 180 seconds.
* Live queries return `"data_label": "STATIC_TIMETABLE"` with `"is_live": false`.

## Immediate Mitigation
1. Check RailRadar or upstream API connectivity:
   ```bash
   curl -i --max-time 5 "https://api.railradar.io/health"
   ```
2. If upstream provider is down, verify that TransitPulse static timetable fallback continues serving commuter queries with degradation warnings.
3. If API keys expired or quota exceeded (HTTP 429), rotate key in environment:
   ```bash
   export RAILRADAR_API_KEY="new_key"
   ```
4. Verify `/api/v1/trains/live/...` returns status code 200 with fallback static data.
