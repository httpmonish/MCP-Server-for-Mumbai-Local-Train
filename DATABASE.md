# TransitPulse Database Schema & Data Models Documentation

## Overview
TransitPulse is designed on **PostgreSQL** using **SQLAlchemy ORM** and **Alembic** migrations. The database enforces multi-tenant row-level isolation via `organization_id`, strict composite foreign key constraints, robust indexing for high-throughput transit queries, and immutable audit logs.

---

## 1. Entity Relationship & Models

### Core Identity & Tenancy (`Phase 1 & 2`)
- **`User`** (`users` table):
  - `id` (UUID, PK)
  - `email` (String, Unique, Index)
  - `hashed_password` (String, Argon2id/Bcrypt hash)
  - `full_name` (String)
  - `is_active` (Boolean)
  - `is_superuser` (Boolean)
  - `created_at`, `updated_at` (DateTime, UTC)

- **`Organization`** (`organizations` table):
  - `id` (UUID, PK)
  - `name` (String)
  - `slug` (String, Unique, Index)
  - `org_type` (Enum: `COLLEGE`, `COMPANY`)
  - `created_at`, `updated_at` (DateTime, UTC)

- **`Member`** (`members` table):
  - `id` (UUID, PK)
  - `user_id` (UUID, FK -> `users.id`)
  - `organization_id` (UUID, FK -> `organizations.id`)
  - `role` (Enum: `STUDENT`, `TEACHER`, `EMPLOYEE`, `HR_ADMIN`, `ORG_ADMIN`)
  - `home_station` (String, Station Code)
  - `destination_station` (String, Station Code)
  - `preferred_transit_line` (String)
  - `is_active` (Boolean)
  - Unique Constraint: `(user_id, organization_id)`

---

### Mumbai Transit Engine (`Phase 3`)
- **`Station`** (`stations` table):
  - `code` (String(10), PK)
  - `name` (String)
  - `latitude`, `longitude` (Float)
  - `zone` (String)

- **`Line`** (`lines` table):
  - `code` (String(10), PK: `WR`, `CR`, `HR`, `TR`)
  - `name` (String)
  - `color_hex` (String)

- **`LineStation`** (`line_stations` table):
  - `id` (UUID, PK)
  - `line_code` (FK -> `lines.code`)
  - `station_code` (FK -> `stations.code`)
  - `sequence` (Integer)
  - `distance_from_origin_km` (Float)

- **`TrainSchedule`** (`train_schedules` table):
  - `train_number` (String(10), PK)
  - `line_code` (FK -> `lines.code`)
  - `train_type` (Enum: `SLOW`, `FAST`, `AC`, `LADIES_SPECIAL`)
  - `source_station_code` (FK -> `stations.code`)
  - `destination_station_code` (FK -> `stations.code`)
  - `departure_time` (Time)
  - `arrival_time` (Time)

- **`TrainStop`** (`train_stops` table):
  - `id` (UUID, PK)
  - `train_number` (FK -> `train_schedules.train_number`)
  - `station_code` (FK -> `stations.code`)
  - `arrival_time` (Time)
  - `departure_time` (Time)
  - `stop_sequence` (Integer)
  - Index: `(train_number, stop_sequence)`, `(station_code, departure_time)`

---

### Schedules & Timetables (`Phase 4`)
- **`Schedule`** (`schedules` table):
  - `id` (UUID, PK)
  - `organization_id` (UUID, FK -> `organizations.id`, Index)
  - `title` (String)
  - `schedule_type` (Enum: `CLASS`, `SHIFT`)
  - `start_date`, `end_date` (Date)
  - `is_active` (Boolean)

- **`ScheduleSlot`** (`schedule_slots` table):
  - `id` (UUID, PK)
  - `schedule_id` (UUID, FK -> `schedules.id`, Index)
  - `day_of_week` (Integer: 0=Mon, 6=Sun)
  - `start_time` (Time)
  - `end_time` (Time)
  - `location` (String)

- **`ScheduleOccurrence`** (`schedule_occurrences` table):
  - `id` (UUID, PK)
  - `schedule_id` (UUID, FK -> `schedules.id`, Index)
  - `slot_id` (UUID, FK -> `schedule_slots.id`)
  - `date` (Date, Index)
  - `start_datetime`, `end_datetime` (DateTime, UTC)
  - `status` (Enum: `SCHEDULED`, `CANCELLED`, `COMPLETED`)

---

### Attendance System (`Phase 5`)
- **`AttendanceRecord`** (`attendance_records` table):
  - `id` (UUID, PK)
  - `organization_id` (UUID, FK -> `organizations.id`, Index)
  - `member_id` (UUID, FK -> `members.id`, Index)
  - `schedule_occurrence_id` (UUID, FK -> `schedule_occurrences.id`, Index)
  - `status` (Enum: `PRESENT`, `ABSENT`, `LATE`, `EXCUSED`)
  - `marked_at` (DateTime, UTC)
  - `marked_by_user_id` (UUID, FK -> `users.id`)
  - Unique Constraint: `(member_id, schedule_occurrence_id)`

- **`AttendanceSummary`** (`attendance_summaries` table):
  - `id` (UUID, PK)
  - `organization_id` (UUID, FK -> `organizations.id`)
  - `member_id` (UUID, FK -> `members.id`)
  - `total_sessions` (Integer)
  - `present_count` (Integer)
  - `absent_count` (Integer)
  - `late_count` (Integer)
  - `attendance_percentage` (Float)
  - Unique Constraint: `(organization_id, member_id)`

---

### Notification Outbox & Event Engine (`Phase 8`)
- **`NotificationOutbox`** (`notification_outbox` table):
  - `id` (UUID, PK)
  - `organization_id` (UUID, FK -> `organizations.id`, Index)
  - `user_id` (UUID, FK -> `users.id`, Index)
  - `event_type` (Enum: `DISRUPTION`, `COMMUTE_RISK`, `ATTENDANCE_WARNING`, `SCHEDULE_CHANGE`)
  - `channel` (Enum: `EMAIL`, `IN_APP`, `PUSH`, `WEBHOOK`)
  - `payload` (JSONB)
  - `idempotency_key` (String, Unique, Index)
  - `status` (Enum: `PENDING`, `SENDING`, `SENT`, `FAILED`, `CANCELLED`)
  - `retry_count` (Integer, Default 0)
  - `max_retries` (Integer, Default 3)
  - `next_retry_at` (DateTime, UTC, Index)
  - `created_at`, `updated_at` (DateTime, UTC)

---

### MCP Audit Log (`Phase 7 & 9`)
- **`MCPAuditLog`** (`mcp_audit_logs` table):
  - `id` (UUID, PK)
  - `session_id` (String)
  - `client_id` (String)
  - `user_id` (UUID, FK -> `users.id`, Nullable)
  - `organization_id` (UUID, FK -> `organizations.id`, Nullable)
  - `tool_name` (String, Index)
  - `parameters` (JSONB, Redacted)
  - `execution_time_ms` (Float)
  - `status` (Enum: `SUCCESS`, `DENIED`, `ERROR`)
  - `error_message` (Text, Safe/Sanitized)
  - `created_at` (DateTime, UTC, Index)

---

## 2. Indexing Strategy
1. **Multi-Tenancy**: `(organization_id, id)` on all tenant entities.
2. **Transit Routing**: `(station_code, departure_time)` for fast next-train timetable scans.
3. **Outbox Polling**: `(status, next_retry_at)` for lock-free outbox worker polling (`SELECT ... FOR UPDATE SKIP LOCKED`).
4. **Attendance Lookups**: `(member_id, date)` and unique index `(member_id, schedule_occurrence_id)`.

---

## 3. Database Maintenance & Housekeeping
- **Connection Pooling**: Recommended pool size 20, max overflow 10.
- **Statement Timeout**: Set `statement_timeout = '15s'` to prevent runaway analytical queries.
- **Migrations**: Always backward-compatible (Nullable columns added first, backfilled, constraints added later).
