# AGENT DIRECTIVE: Phase 11 — Real-Time WebSocket Streaming, Crowdsourced Delay Intelligence & Zero-Trust Credential Encryption

You are a Principal Distributed Systems & Security Architect. Implement Phase 11 of the `mcp-data-server`. Your objective is to elevate this system to enterprise tier by building:
1. **Zero-Trust AES-256-GCM Envelope Encryption** for secure at-rest storage of student portal credentials.
2. **Real-Time WebSocket Gateway** backed by Redis Pub/Sub for broadcasting commute disruptions and live departure ticks without HTTP polling.
3. **Crowdsourced Transit Delay Consensus Engine** using a time-decayed Bayesian scoring algorithm to validate commuter-reported train delays.

Every file below must be written in full production quality. Do not use placeholders, dummy print statements, or omitted error handling.

---

## 1. ENVIRONMENT & DEPENDENCIES
Install cryptography and real-time streaming dependencies in your active virtual environment:
```bash
pip install cryptography websockets redis pytest pytest-asyncio
```

---

## 2. FILE-BY-FILE PRODUCTION SPECIFICATIONS

### File 1: `backend/app/core/crypto.py`
Implement authenticated envelope encryption using AES-256-GCM.

### File 2: `backend/app/models/transit_delay.py`
Define SQLAlchemy models for real-time commuter delay reports.

### File 3: `backend/app/services/delay_consensus.py`
Implement the time-decayed consensus algorithm to aggregate multiple commuter reports into a single verified delay metric.

### File 4: `backend/app/services/websocket_manager.py`
Implement a high-throughput, multi-client connection manager backed by Redis Pub/Sub channels to broadcast disruption updates horizontally.

### File 5: `backend/app/routes/delays.py`
Expose delay reporting and real-time streaming endpoints.

---

## 3. UNIT & RESILIENCE TEST SPECIFICATIONS

### File 6: `backend/tests/test_crypto.py`
### File 7: `backend/tests/test_delay_consensus.py`
### File 8: `backend/tests/test_websocket_stream.py`

---

## 4. VERIFICATION COMMANDS

Execute the test suite to validate cryptography, consensus algorithms, and streaming:
```bash
pytest backend/tests/test_crypto.py backend/tests/test_delay_consensus.py backend/tests/test_websocket_stream.py -v
```
