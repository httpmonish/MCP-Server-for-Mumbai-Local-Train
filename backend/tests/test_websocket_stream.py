import asyncio
import json

from app.main import app
from app.routes.delays import ws_manager
from fastapi.testclient import TestClient


def test_websocket_ping_pong_heartbeat():
    client = TestClient(app)
    with client.websocket_connect("/api/v1/delays/ws/transit/CR") as websocket:
        websocket.send_text("ping")
        response = websocket.receive_text()
        assert response == "pong"


def test_websocket_broadcast_delay_event():
    client = TestClient(app)
    with client.websocket_connect("/api/v1/delays/ws/transit/CR") as websocket:
        event_payload = {
            "event_type": "DELAY_UPDATE",
            "train_number": "97005",
            "station_code": "TNA",
            "corridor": "CR",
            "consensus": {
                "verified": True,
                "delay_minutes": 15,
                "confidence": 3.2,
                "report_count": 4,
            },
        }

        # Broadcast to local connected sockets
        asyncio.run(ws_manager.broadcast_local("CR", event_payload))

        received_text = websocket.receive_text()
        payload = json.loads(received_text)

        assert payload["event_type"] == "DELAY_UPDATE"
        assert payload["train_number"] == "97005"
        assert payload["station_code"] == "TNA"
        assert payload["consensus"]["verified"] is True
        assert payload["consensus"]["delay_minutes"] == 15
