# Security Baseline & OWASP Threat Mitigation Matrix

## 1. Authentication & Token Management
* **Password Hashing**: Bcrypt with salt rounds = 12 and 72-byte truncation boundary.
* **JWT Access Tokens**: Signed using HS256 with minimum 32-character secret key. Expiration is 15 minutes. Contains strict claims: `sub`, `email`, `org_id`, `role`, `jti`, `iat`, `exp`.
* **Refresh Tokens**: Cryptographically secure 48-byte random opaque tokens stored with SHA-256 hash in Redis. Single-use rotation on refresh with automatic revocation upon reuse detection.

---

## 2. Multi-Tenant Isolation & IDOR Defense
* Every SQL query across `organizations`, `members`, `schedules`, `attendance`, `outbox_events`, and `notifications` includes explicit `org_id` filtering from the authenticated JWT context.
* Cross-tenant access attempts return `403 Forbidden` or `404 Not Found` without revealing resource existence.
* Administrative roles (`ORG_ADMIN`, `TEACHER`, `HR_ADMIN`) are constrained strictly within their own `org_id`.

---

## 3. OWASP API Security Top 10 Mitigation Matrix

| OWASP Vulnerability | TransitPulse Defense Mechanism | Automated Test Reference |
| :--- | :--- | :--- |
| **API1:2023 - Broken Object Level Authorization (BOLA/IDOR)** | Scoped multi-tenant queries by `org_id` and user ownership. | `test_cross_tenant_strict_isolation`, `test_cross_tenant_idor_security` |
| **API2:2023 - Broken Authentication** | Token hashing in Redis, algorithm confusion defense, refresh rotation, rate-limited login. | `test_jwt_algorithm_confusion_attack`, `test_token_refresh_rotation` |
| **API3:2023 - Broken Object Property Level Authorization** | Explicit Pydantic input schemas; mass assignment on `role`, `org_id`, `created_at` prohibited. | `test_member_guards_and_constraints` |
| **API4:2023 - Unrestricted Resource Consumption** | SlowAPI rate limiters (10/min default, 5/min login, 30/min MCP, 60/min notifications). | `test_rate_limiter_triggers_429` |
| **API5:2023 - Broken Function Level Authorization (BFLA)** | Role-based access control (`UserRole.PLATFORM_ADMIN`, `ORG_ADMIN`, `STUDENT`) enforced on routes. | `test_role_escalation_prevention` |
| **API6:2023 - Server-Side Request Forgery (SSRF)** | External endpoints restricted strictly to configured domains (SendGrid, RailRadar). No arbitrary URLs accepted. | `test_mcp_prompt_injection_sanitization` |
| **API7:2023 - Security Misconfiguration** | Startup validator fails if `JWT_SECRET_KEY < 32` chars or `DEBUG=True`. Production security headers enforced. | `test_observability_middleware_headers_and_correlation` |
| **API8:2023 - Lack of Protection from Automated Threats** | Rate limiting, brute-force login delays, honeypot headers. | `test_login_invalid_credentials` |
| **API9:2023 - Improper Inventory Management** | OpenAPI spec versioned at `/api/v1/`. MCP endpoints partitioned at `/mcp`. | `test_mcp_server_tool_discovery` |
| **API10:2023 - Unsafe Consumption of APIs** | Contract validation for RailRadar and SendGrid responses with timeouts and circuit fallback. | `test_railradar_provider_resilience_and_graceful_handling` |

---

## 4. Input Sanitization & CSV Injection Defense
* CSV bulk uploads sanitize spreadsheet formula prefixes (`=`, `+`, `-`, `@`, `\t`, `\r`) to prevent formula execution in Excel/Sheets.
* Maximum upload size is enforced (max 5MB, max 5,000 rows per batch).
