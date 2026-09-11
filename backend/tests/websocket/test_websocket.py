from app.extensions import socketio
from app.models.company import Company
from app.models.device import Device
from app.websocket.events import EVENT_AGENT_HEARTBEAT, EVENT_AGENT_HEARTBEAT_ACK

def test_websocket_agent_heartbeat(app):
    with app.app_context():
        company = Company.query.first()
        test_client = socketio.test_client(app)
        assert test_client.is_connected()

        # Emit agent heartbeat
        payload = {
            "device_uid": "WS-UID-SOCKET-001",
            "company_id": company.id,
            "hostname": "WS-SOCKET-TEST",
            "status": "ACTIVE",
            "agent_version": "1.2.0"
        }
        test_client.emit(EVENT_AGENT_HEARTBEAT, payload)

        # Receive ACK
        received = test_client.get_received()
        ack_events = [e for e in received if e["name"] == EVENT_AGENT_HEARTBEAT_ACK]
        assert len(ack_events) > 0
        assert ack_events[0]["args"][0]["status"] == "ACK"

        # Verify device in DB
        device = Device.query.filter_by(device_uid="WS-UID-SOCKET-001").first()
        assert device is not None
        assert device.hostname == "WS-SOCKET-TEST"
        assert device.status == "ACTIVE"
