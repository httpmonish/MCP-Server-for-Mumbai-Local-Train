#!/usr/bin/env bash
set -euo pipefail

TARGET_HOST="${1:-http://localhost:8000}"
echo "=================================================="
echo "Executing Deployment Smoke Tests against: ${TARGET_HOST}"
echo "=================================================="

echo "[1/4] Checking Liveness Probe (/health)..."
LIVENESS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${TARGET_HOST}/health")
if [ "$LIVENESS_STATUS" -eq 200 ]; then
  echo "PASS: /health returned HTTP 200"
else
  echo "FAIL: /health returned HTTP ${LIVENESS_STATUS}"
  exit 1
fi

echo "[2/4] Checking Readiness Probe (/ready)..."
READINESS_RESPONSE=$(curl -s "${TARGET_HOST}/ready")
if echo "$READINESS_RESPONSE" | grep -q '"database":"connected"' && echo "$READINESS_RESPONSE" | grep -q '"redis":"connected"'; then
  echo "PASS: PostgreSQL and Redis connections verified."
else
  echo "FAIL: Readiness probe output degraded: ${READINESS_RESPONSE}"
  exit 1
fi

echo "[3/4] Testing Train Route Query API..."
TRAIN_HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${TARGET_HOST}/api/v1/trains/next?from_station=CSMT&to_station=BY")
if [ "$TRAIN_HTTP_STATUS" -eq 200 ]; then
  echo "PASS: /api/v1/trains/next returned HTTP 200"
else
  echo "FAIL: /api/v1/trains/next returned HTTP ${TRAIN_HTTP_STATUS}"
  exit 1
fi

echo "[4/4] Verifying Rate-Limiting Engine..."
BURST_BLOCKED=false
for i in {1..25}; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${TARGET_HOST}/api/v1/academic/attendance/SMOKE_TEST" \
    -H "Content-Type: application/json" \
    -d '{"username":"smoke","password":"test"}')
  if [ "$CODE" -eq 429 ]; then
    BURST_BLOCKED=true
    break
  fi
done

if [ "$BURST_BLOCKED" = true ]; then
  echo "PASS: Rate limiter successfully intercepted burst requests (HTTP 429 received)."
else
  echo "FAIL: Rate limiter failed to block excessive requests."
  exit 1
fi

echo "=================================================="
echo "ALL DEPLOYMENT SMOKE TESTS PASSED SUCCESSFULLY"
echo "=================================================="
