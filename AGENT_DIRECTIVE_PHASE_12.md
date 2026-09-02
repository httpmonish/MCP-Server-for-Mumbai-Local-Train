# AGENT DIRECTIVE: Phase 12 — Multi-Campus Adapter Federation, Local Edge SLM Inference & Chaos Resilience Suite

You are an Enterprise Solutions Architect and Chaos Engineering Specialist. Implement Phase 12 of the `mcp-data-server`. Your objective is to scale the system beyond a single institution and cloud dependency by building:
1. **Dynamic Multi-Campus Scraper Federation:** An extensible Plugin/Adapter Strategy pattern dynamically resolving distinct university portals (e.g., Mumbai University, autonomous college portals) via runtime registry.
2. **Local Edge SLM (Small Language Model) Function-Calling Gateway:** An offline inference bridge interfacing with Ollama / llama.cpp for on-device tool calling when internet access or Anthropic cloud access is unavailable.
3. **Automated Chaos Engineering Suite:** Automated fault-injection harnesses simulating network degradation, scraper deadlocks, database partitions, and memory exhaustion to verify zero-downtime self-healing.

Every file below must be written in full production quality. Do not use placeholders, dummy stub methods, or unhandled exceptions.

---

## 1. ENVIRONMENT & DEPENDENCIES
Install local model interfaces, chaos injection, and load-testing dependencies in the virtual environment:
```bash
pip install ollama litellm locust pytest pytest-asyncio psutil
```

---

## 2. FILE-BY-FILE PRODUCTION SPECIFICATIONS

### File 1: `backend/app/scrapers/base_adapter.py`
Define the abstract university portal strategy interface using Python `abc`.

### File 2: `backend/app/scrapers/adapters/mu_standard.py`
Implement the standard University of Mumbai ERP adapter.

### File 3: `backend/app/local_ai/edge_gateway.py`
Implement an offline-first Small Language Model (SLM) gateway using Ollama for local device inference.

### File 4: `backend/app/chaos/fault_injector.py`
Implement a production chaos engineering engine simulating catastrophic runtime conditions.

### File 5: `backend/tests/chaos/test_system_resilience.py`
Write end-to-end chaos integration tests verifying self-healing behavior under active fault injection.

### File 6: `backend/scripts/disaster_recovery.sh`
Automate backup generation, database recovery, and integrity validation.

---

## 3. VERIFICATION COMMANDS

Execute the multi-campus registry, local SLM test suite, and chaos resilience suite:
```bash
pytest backend/tests/chaos/test_system_resilience.py -v
bash backend/scripts/disaster_recovery.sh
```
