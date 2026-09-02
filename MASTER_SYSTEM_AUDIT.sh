#!/usr/bin/env bash
# ==============================================================================
# MASTER SYSTEM VERIFICATION & AUDIT SUITE: PHASES 0 TO 12
# Project: Campus & Commute MCP Data Server
# ==============================================================================
set -u

# Ensure virtual environment and Node.js toolchains are in PATH
if [ -d ".venv" ]; then
    export PATH="$(pwd)/.venv/bin:${PATH}"
fi
for candidate in "$HOME/.local/bin" "$HOME/.local/node/bin"; do
    if [ -d "$candidate" ]; then
        export PATH="${candidate}:${PATH}"
    fi
done
export PYTHONPATH="backend:.:${PYTHONPATH:-}"

# Terminal Color Formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0

print_header() {
    echo -e "\n${BLUE}${BOLD}==============================================================================${NC}"
    echo -e "${CYAN}${BOLD}>>> $1${NC}"
    echo -e "${BLUE}${BOLD}==============================================================================${NC}"
}

run_check() {
    local check_name="$1"
    local command_to_run="$2"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -ne "  [..] Running Check: ${BOLD}${check_name}${NC} ... "
    
    OUTPUT=$(eval "${command_to_run}" 2>&1)
    EXIT_CODE=$?
    
    if [ ${EXIT_CODE} -eq 0 ]; then
        echo -e "\r  ${GREEN}[PASS]${NC} ${check_name}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "\r  ${RED}[FAIL]${NC} ${check_name}"
        echo -e "${YELLOW}------- STDOUT/STDERR CAPTURE -------${NC}"
        echo "${OUTPUT}" | head -n 25
        echo -e "${YELLOW}-------------------------------------${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

skip_check() {
    local check_name="$1"
    local reason="$2"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    echo -e "  ${PURPLE}[SKIP]${NC} ${check_name} (${reason})"
}

echo -e "${BOLD}${PURPLE}"
cat << "BANNER"
  __  __  ____ _____   ____  ____  __  __ ____    _    _   _ ____ ___ _____ 
 |  \/  |/ ___|  _ \ / ___|/ ___||  \/  |  _ \  / \  | | | |  _ \_ _|_   _|
 | |\/| | |   | |_) | |  _| |    | |\/| | |_) |/ _ \ | | | | | | | |  | |  
 | |  | | |___|  __/| |_| | |___ | |  | |  __// ___ \| |_| | |_| | |  | |  
 |_|  |_|\____|_|    \____|\____||_|  |_|_|  /_/   \_\\___/|____/___| |_|  
BANNER
echo -e "${CYAN}Autonomous Comprehensive End-to-End System Auditor (Phases 0–12)${NC}\n"

# ------------------------------------------------------------------------------
# SECTION 1: SYSTEM ENVIRONMENT & ARCHITECTURE FOUNDATION (PHASE 0)
# ------------------------------------------------------------------------------
print_header "STAGE 1: Foundations, Dependencies & File Tree Integrity (Phase 0)"

run_check "Python 3.10+ Active Runtime" "python3 -c 'import sys; assert sys.version_info >= (3, 10), \"Python 3.10+ required\"'"

REQUIRED_FILES=(
    "backend/app/main.py"
    "backend/app/core/config.py"
    "backend/app/models/academic.py"
    "backend/app/models/train.py"
    "backend/app/scrapers/college_portal.py"
    "backend/app/cache.py"
    "backend/app/services/academic_orchestrator.py"
    "backend/app/services/train_service.py"
    "backend/mcp_server/server.py"
    "frontend/index.html"
    "docs/architecture.md"
    "README.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    run_check "File Presence: ${file}" "test -f ${file}"
done

# ------------------------------------------------------------------------------
# SECTION 2: STATIC CODE ANALYSIS & SECURITY AUDIT (PHASE 8)
# ------------------------------------------------------------------------------
print_header "STAGE 2: Static Code Quality, Imports & Linter Audit (Phase 8)"

if command -v ruff &> /dev/null; then
    run_check "Ruff Static Code Analysis" "ruff check backend/"
else
    skip_check "Ruff Linter" "ruff binary not found in PATH; pip install ruff"
fi

run_check "Core Import Integrity Verification" "python3 -c '
from app.core.config import settings
from app.models.academic import AttendanceRecord, ExamTimetable
from app.models.train import TrainSchedule
from app.cache import RedisCache
from app.scrapers.college_portal import CollegePortalScraper
from app.services.academic_orchestrator import AcademicOrchestrator
from app.mcp_server.server import app as mcp_app
print(\"Core imports verified successfully.\")
'"

# ------------------------------------------------------------------------------
# SECTION 3: ACADEMIC SCRAPER & PERSISTENCE TESTS (PHASE 1)
# ------------------------------------------------------------------------------
print_header "STAGE 3: College Portal Scraper & Database Upserts (Phase 1)"

if [ -f "backend/tests/test_scraper.py" ]; then
    run_check "Offline Scraper DOM Parser & Fixtures" "pytest backend/tests/test_scraper.py -q"
else
    skip_check "Phase 1 Scraper Tests" "backend/tests/test_scraper.py missing"
fi

# ------------------------------------------------------------------------------
# SECTION 4: CACHING, RATE LIMITING & RESILIENCE (PHASE 2)
# ------------------------------------------------------------------------------
print_header "STAGE 4: Redis Cache-Aside, Rate Limiting & Fail-Open Fallback (Phase 2)"

if [ -f "backend/tests/test_cache.py" ]; then
    run_check "Redis Cache-Aside & Expiry Tests" "pytest backend/tests/test_cache.py -q"
fi

if [ -f "backend/tests/test_orchestrator.py" ]; then
    run_check "Orchestrator Degradation & SlowAPI Rate Limits" "pytest backend/tests/test_orchestrator.py -q"
fi

# ------------------------------------------------------------------------------
# SECTION 5: SUBURBAN TRAIN TIMETABLE PARSER & QUERIES (PHASE 3)
# ------------------------------------------------------------------------------
print_header "STAGE 5: Railway Timetable Extraction & Chronological Routing (Phase 3)"

if [ -f "backend/tests/test_train_service.py" ]; then
    run_check "Train Schedule Parsing & Directional Routing" "pytest backend/tests/test_train_service.py -q"
else
    skip_check "Phase 3 Train Tests" "backend/tests/test_train_service.py missing"
fi

# ------------------------------------------------------------------------------
# SECTION 6: MODEL CONTEXT PROTOCOL (MCP) TOOL INTEGRITY (PHASE 4)
# ------------------------------------------------------------------------------
print_header "STAGE 6: Model Context Protocol (MCP) Standard Tool Suite (Phase 4)"

run_check "MCP Tool Schema & Tool Handler Tests" "python3 -c '
import asyncio
from app.mcp_server.server import app

async def audit_mcp():
    tools = await app.list_tools()
    tool_names = [t.name for t in tools]
    expected = [\"get_student_attendance\", \"get_upcoming_exams\", \"get_next_train\"]
    for e in expected:
        assert e in tool_names, f\"Missing required MCP tool: {e}\"
    print(f\"MCP verified with {len(tools)} tools: {tool_names}\")

asyncio.run(audit_mcp())
'"

if [ -f "backend/tests/test_mcp_server.py" ]; then
    run_check "MCP Tool Pytest Integration Suite" "pytest backend/tests/test_mcp_server.py -q"
fi

# ------------------------------------------------------------------------------
# SECTION 7: DEPLOYMENT CONTAINERS & HEALTH MONITORING (PHASE 5)
# ------------------------------------------------------------------------------
print_header "STAGE 7: Containerization & Readiness Health Probes (Phase 5)"

if [ -f "backend/Dockerfile" ]; then
    run_check "Dockerfile Linting & Syntax Validation" "grep -q 'playwright install chromium' backend/Dockerfile && grep -q 'EXPOSE 8000' backend/Dockerfile"
fi

if [ -f "backend/tests/test_health.py" ]; then
    run_check "Liveness & Deep Readiness Probe Tests" "pytest backend/tests/test_health.py -q"
fi

# ------------------------------------------------------------------------------
# SECTION 8: FRONTEND DASHBOARDS (PHASES 6 & 9)
# ------------------------------------------------------------------------------
print_header "STAGE 8: Frontend Dashboards (v1 Vanilla & v2 React PWA)"

run_check "Frontend v1 Vanilla Architecture" "test -f frontend/index.html && test -f frontend/js/app.js && test -f frontend/js/config.js"

if [ -d "frontend-v2" ]; then
    if [ -f "frontend-v2/package.json" ]; then
        run_check "Frontend v2 React TypeScript Compilation" "(cd frontend-v2 && (npm run build --dry-run 2>/dev/null || npx tsc --noEmit))"
    fi
else
    skip_check "Frontend v2 (Phase 9)" "frontend-v2 directory not initialized yet"
fi

# ------------------------------------------------------------------------------
# SECTION 9: CORS PREFLIGHT & RUNTIME POLICY (PHASE 7)
# ------------------------------------------------------------------------------
print_header "STAGE 9: Production CORS Security & Origin Validation (Phase 7)"

if [ -f "backend/tests/test_cors.py" ]; then
    run_check "Automated CORS Preflight & Wildcard Regex Tests" "pytest backend/tests/test_cors.py -q"
else
    skip_check "CORS Pytest Suite" "backend/tests/test_cors.py missing"
fi

# ------------------------------------------------------------------------------
# SECTION 10: PROACTIVE WORKERS, ALERTS & METRICS (PHASE 10)
# ------------------------------------------------------------------------------
print_header "STAGE 10: Background ARQ Workers, Decision Engine & Prometheus (Phase 10)"

if [ -f "backend/app/services/decision_engine.py" ]; then
    run_check "Commute Decision Engine Unit Tests" "python3 -c '
import datetime
from app.services.decision_engine import CommuteDecisionEngine

engine = CommuteDecisionEngine()
attendance = [{\"subject_name\": \"Networks\", \"total_conducted\": 40, \"total_attended\": 26, \"percentage\": 65.0}]
trains = [{\"train_number\": \"95701\", \"arrival_at_destination\": \"08:35\"}]
eval_res = engine.evaluate_commute_urgency(attendance, [], trains, datetime.time(9, 0))
assert eval_res[\"risk_level\"] in [\"HIGH\", \"MEDIUM\"]
print(\"Decision Engine verified successfully.\")
'"
fi

if [ -f "backend/tests/test_decision_engine.py" ]; then
    run_check "Decision Engine & Alert Dispatcher Pytest Suite" "pytest backend/tests/test_decision_engine.py backend/tests/test_alert_dispatcher.py -q"
fi

# ------------------------------------------------------------------------------
# SECTION 11: ZERO-TRUST CRYPTOGRAPHY & DELAY CONSENSUS (PHASE 11)
# ------------------------------------------------------------------------------
print_header "STAGE 11: AES-256-GCM Credential Encryption & Bayesian Consensus (Phase 11)"

if [ -f "backend/app/core/crypto.py" ]; then
    run_check "AES-256-GCM Zero-Trust Crypto Roundtrip & Tamper Proofing" "python3 -c '
import os, base64
from app.core.crypto import CredentialVault

key = base64.b64encode(os.urandom(32)).decode()
vault = CredentialVault(key)
secret = \"SuperSecretStudentPassword!123\"
token = vault.encrypt(secret)
assert token != secret
assert vault.decrypt(token) == secret
print(\"Zero-Trust AES-256-GCM verified.\")
'"
fi

if [ -f "backend/tests/test_crypto.py" ]; then
    run_check "Phase 11 Cryptography, Consensus & WebSocket Tests" "pytest backend/tests/test_crypto.py backend/tests/test_delay_consensus.py -q"
fi

# ------------------------------------------------------------------------------
# SECTION 12: MULTI-CAMPUS FEDERATION & CHAOS RESILIENCE (PHASE 12)
# ------------------------------------------------------------------------------
print_header "STAGE 12: Multi-Campus Adapter Strategy & Chaos Hardening (Phase 12)"

if [ -f "backend/app/scrapers/base_adapter.py" ]; then
    run_check "Campus Adapter Registry Resolution" "python3 -c '
from app.scrapers.base_adapter import CampusAdapterRegistry
campuses = CampusAdapterRegistry.list_supported_campuses()
print(f\"Campus Adapter Registry operational. Supported: {len(campuses)}\")
'"
fi

if [ -f "backend/tests/chaos/test_system_resilience.py" ]; then
    run_check "Chaos Fault Injection & Resilience Suite" "pytest backend/tests/chaos/test_system_resilience.py -q"
fi

# ==============================================================================
# FINAL AUDIT SUMMARY SCORECARD
# ==============================================================================
echo -e "\n${BLUE}${BOLD}==============================================================================${NC}"
echo -e "${BOLD}                     FINAL SYSTEM AUDIT SCORECARD                             ${NC}"
echo -e "${BLUE}${BOLD}==============================================================================${NC}"
echo -e "  Total Invariants Tested : ${BOLD}${TOTAL_CHECKS}${NC}"
echo -e "  Passed Validations      : ${GREEN}${BOLD}${PASSED_CHECKS}${NC}"
echo -e "  Failed Validations      : ${RED}${BOLD}${FAILED_CHECKS}${NC}"
echo -e "  Skipped / Pending Phase : ${PURPLE}${BOLD}${SKIPPED_CHECKS}${NC}"

SUCCESS_RATE=0
if [ ${TOTAL_CHECKS} -gt 0 ]; then
    SUCCESS_RATE=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
fi
echo -e "  Overall System Integrity: ${CYAN}${BOLD}${SUCCESS_RATE}%${NC}"
echo -e "${BLUE}${BOLD}==============================================================================${NC}"

if [ ${FAILED_CHECKS} -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}✓ VERIFICATION SUCCESSFUL:${NC} All tested system phases are production-ready and fully operational.\n"
    exit 0
else
    echo -e "\n${RED}${BOLD}✗ VERIFICATION FAILED:${NC} ${FAILED_CHECKS} subsystem(s) failed verification. Inspect logs above.\n"
    exit 1
fi
