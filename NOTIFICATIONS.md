# TransitPulse Notification & Alerting Engine

## 1. Outbox Pattern Architecture
TransitPulse decouples notification emission from HTTP request lifecycles using the **Transactional Outbox Pattern**:

```
+-------------------------------------------------------+
| FastAPI Request / Attendance / Intelligence Engine    |
| (Inserts Domain Event + Outbox Record in same DB Tx)  |
+---------------------------+---------------------------+
                            |
                            v
               +-------------------------+
               |  PostgreSQL DB Outbox   |
               | (notification_outbox)   |
               +------------+------------+
                            |
            SELECT ... FOR UPDATE SKIP LOCKED
                            |
                            v
               +-------------------------+
               |   Notification Worker   |
               | (Idempotency & Retries) |
               +------------+------------+
                            |
           +----------------+----------------+
           |                                 |
           v                                 v
   +---------------+                 +---------------+
   | Email Provider|                 | Webhook / InApp|
   | (SendGrid/SES)|                 | Dispatcher    |
   +---------------+                 +---------------+
```

## 2. Key Reliability & Security Features
- **Strict Deduplication & Idempotency**: Each notification has a deterministic `idempotency_key` (e.g. `commute_risk:{member_id}:{occurrence_id}:{date}`).
- **Lock-Free Concurrency**: Background workers select rows using `SELECT ... FOR UPDATE SKIP LOCKED`, preventing double delivery across multiple worker pods.
- **Exponential Backoff with Jitter**: Failed deliveries are retried at $2^{\text{retry\_count}} \times 30\text{s} \pm \text{jitter}$ up to `max_retries = 3`.
- **Tenant Isolation**: Users only receive notifications for organizations they actively belong to.
- **PII Protection**: Notification payloads redact passwords, authorization tokens, and precise coordinates before logging.
