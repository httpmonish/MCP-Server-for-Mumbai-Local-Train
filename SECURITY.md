# Security Policy & Hardening Baseline

## 1. Multi-Tenant Authorization Security
* All tenant-scoped operations enforce explicit `org_id` equality checks against the authenticated JWT context.
* Organization administrators cannot view, modify, or delete members, schedules, attendance records, or notifications belonging to other organizations.
* Automated IDOR tests (`test_cross_tenant_strict_isolation`, `test_cross_tenant_idor_security`) continuously verify cross-tenant access denial.

---

## 2. Secrets & Credential Protection
* **No hardcoded secrets**: All API keys, database credentials, and signing secrets are strictly managed via environment variables in `Settings`.
* **Log Redaction**: Standardized logging uses `SecretRedactionFilter` to scrub passwords, Bearer tokens, and API keys.
* **Token Storage**: Refresh tokens are stored with cryptographic SHA-256 hashes in Redis.

---

## 3. Defense Against Automated Threats & Input Injection
* **Rate Limiting**: SlowAPI limits login attempts (5/min), MCP queries (30/min), and general API traffic (10/min default).
* **CSV Formula Injection**: Leading spreadsheet formula operators (`=`, `+`, `-`, `@`) in member import files are sanitized.
* **Template Injection**: Notification templates use strict parameter interpolation with HTML escaping; Python `eval()` is strictly prohibited.
