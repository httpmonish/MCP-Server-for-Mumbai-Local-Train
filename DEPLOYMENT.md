# TransitPulse Deployment & Environment Guide

## 1. Production Container Build
TransitPulse uses multi-stage, non-root Docker containers for minimal surface area:

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
COPY --from=builder /root/.local /home/appuser/.local
COPY . /app
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 2. Environment Variables Configuration
| Variable | Description | Default / Production Value |
|---|---|---|
| `ENVIRONMENT` | Deployment stage | `production` / `staging` |
| `DEBUG` | Verbose debug mode | `false` (Mandatory in production) |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://user:pass@host:5432/dbname` |
| `REDIS_URL` | Redis cache connection string | `redis://:pass@host:6379/0` |
| `SECRET_KEY` | JWT signing secret (min 32 chars) | Managed via Vault / Cloud Secrets |
| `ALLOWED_CORS_ORIGINS` | Comma-separated allowed origins | `https://transitpulse.app,https://admin.transitpulse.app` |
| `SENTRY_DSN` | Sentry Error Reporting DSN | `https://key@sentry.io/project` |
| `SECURITY_HEADERS_ENABLED` | Enable strict security headers | `true` |

## 3. Production Deployment Gates
1. **CI Pipeline Pass**: Linting (Ruff), Type checking, 100% pytest pass rate, and Security SAST (Bandit, pip-audit).
2. **Database Migration**: Run `alembic upgrade head` before switching traffic to new container instances.
3. **Readiness Probe**: Kubernetes / ECS verifies `GET /ready` returns HTTP 200 (PostgreSQL and Redis connectivity confirmed).
4. **Traffic Switch**: Rolling update or Blue/Green deployment with zero downtime.
