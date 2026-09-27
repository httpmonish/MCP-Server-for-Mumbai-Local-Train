# Mumbai Transit Data & Intelligence Engine Documentation

## 1. Architecture Overview
TransitPulse provides real-time and static Mumbai Suburban Railway transit intelligence across Western (WR), Central (CR), Harbour (HR), and Trans-Harbour (TR) lines.

```
                      +-----------------------------+
                      |   Transit Service Gateway   |
                      +--------------+--------------+
                                     |
              +----------------------+----------------------+
              |                                             |
              v                                             v
     +-----------------+                           +-----------------+
     | Redis Cache L1  | (TTL 60s)                 |  Static Engine  |
     +--------+--------+                           | (Postgres/CSV)  |
              | (Cache Miss)                       +--------+--------+
              v                                             |
     +-----------------+                                    |
     | Live Provider   |                                    |
     | (RailRadar API) |                                    |
     +--------+--------+                                    |
              | (Timeout / 5xx / 429 / Stale)               |
              +---------------------------------------------+
                                     |
                                     v
                      +-----------------------------+
                      | Deterministic Commuter Calc |
                      +-----------------------------+
```

## 2. Multi-Tier Fallback & Degradation Strategy
1. **Tier 1 (Real-Time Live)**: Query Redis Cache. If miss, query upstream RailRadar / m-Indicator provider. If response is valid and fresh ($\le 300\text{s}$), update Redis cache and return live delays.
2. **Tier 2 (Cached State)**: If live provider fails with timeout/429/500, return latest cached train state with `is_live=False` and `data_freshness_seconds`.
3. **Tier 3 (Static Timetable Fallback)**: If provider is completely down and cache is expired, seamlessly fallback to deterministic static Mumbai suburban timetable schedules stored in PostgreSQL. The system returns valid arrival/departure estimates with `is_fallback=True`.

## 3. Data Freshness & Provider Contract
- **Contract Schema**: Validates train number, current station, speed km/h, delay minutes, and last update timestamp.
- **Stale Data Detection**: Observations older than 15 minutes are marked `is_stale=True` and trigger degraded confidence weighting in commute recommendations.
- **Circuit Breaker**: If live provider fails 5 times consecutively within 60 seconds, circuit opens for 30 seconds to prevent cascading latency and downstream hammering.
