# TransitPulse Platform — Complete API Reference

## 1. System & Observability Endpoints
* `GET /health` — Liveness check.
* `GET /ready` — Readiness check (verifies PostgreSQL and Redis connectivity).
* `GET /metrics` — Prometheus telemetry scrape endpoint.

---

## 2. Authentication & Identity (Phase 1)
* `POST /auth/register` — Register a new tenant organization and initial administrator user.
* `POST /auth/login` — Authenticate with email and password to obtain access and refresh tokens.
* `POST /auth/refresh` — Rotate single-use refresh token and receive a fresh access token.
* `POST /auth/logout` — Revoke active refresh token session.
* `GET /auth/me` — Retrieve current authenticated user profile and tenant information.

---

## 3. Organizations & Members (Phase 2)
* `GET /organizations/me` — Retrieve tenant organization details.
* `PATCH /organizations/me` — Update organization details (Admin only).
* `POST /organizations/members` — Add an individual member (Teacher, Student, Employee, Admin).
* `GET /organizations/members` — List organization members with pagination and role filters.
* `DELETE /organizations/members/{id}` — Soft delete or remove a member.
* `POST /organizations/members/bulk` — Upload CSV to bulk import members with format validation.

---

## 4. Mumbai Transit & Timetables (Phase 3)
* `GET /api/v1/trains/lines` — List Mumbai suburban railway lines (CR, WR, HR).
* `GET /api/v1/trains/stations` — Query suburban stations with line filter and search.
* `GET /api/v1/trains/schedule` — Retrieve static timetable routes between two stations.
* `GET /api/v1/trains/next` — Retrieve next available trains with real-time/static fallback.
* `GET /api/v1/trains/live/train/{train_number}` — Real-time train telemetry.
* `GET /api/v1/trains/live/station/{station_code}` — Real-time station arrival/departure board.

---

## 5. Schedule & Timetables (Phase 4)
* `POST /api/v1/schedules/locations` — Create campus/office location with nearest station mapping.
* `GET /api/v1/schedules/locations` — List organization locations.
* `POST /api/v1/schedules` — Create a recurring class schedule or shift with slots.
* `GET /api/v1/schedules` — List schedules in organization.
* `POST /api/v1/schedules/assignments` — Assign user to a schedule.
* `GET /api/v1/schedules/me/today` — Retrieve current day schedule occurrences for user.
* `GET /api/v1/schedules/me/week` — Retrieve 7-day chronological schedule matrix for user.

---

## 6. Attendance Engine (Phase 5)
* `POST /api/v1/attendance/policy` — Create/update minimum attendance threshold policy.
* `GET /api/v1/attendance/policy` — Get active policy.
* `POST /api/v1/attendance` — Mark attendance for a single session.
* `POST /api/v1/attendance/bulk` — Mark attendance for multiple students/employees in a slot.
* `GET /api/v1/attendance/me` — Get session-by-session attendance records for authenticated user.
* `GET /api/v1/attendance/me/summary` — Get percentage, total classes, and deficit calculation.
* `PATCH /api/v1/attendance/{id}` — Correct attendance record with audit reason (Admin/Teacher).

---

## 7. Commute & Attendance Intelligence (Phase 6)
* `GET /api/v1/intelligence/commute-check` — Deterministic evaluation combining upcoming class/shift, train status, walking buffer, and attendance deficit.

---

## 8. Model Context Protocol Server (Phase 7)
* `GET /mcp/tools` — Tool schema discovery.
* `POST /mcp/tools/{tool_name}` — Execute read-only tool (`get_my_schedule`, `get_attendance_summary`, `get_next_train`, `check_commute_risk`).

---

## 9. Notification Engine (Phase 8)
* `GET /api/v1/notifications/me` — Get paginated notification history.
* `GET /api/v1/notifications/preferences` — Get user notification channel preferences.
* `PATCH /api/v1/notifications/preferences` — Update channel preferences and quiet hours.
