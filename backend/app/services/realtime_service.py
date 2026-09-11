import json
import logging
from datetime import datetime, timezone
from app.extensions import socketio, redis_client
from app.websocket.events import (
    EVENT_DEVICE_REGISTERED,
    EVENT_DEVICE_ONLINE,
    EVENT_DEVICE_OFFLINE,
    EVENT_DEVICE_STALE,
    EVENT_HEARTBEAT_RECEIVED,
    EVENT_AGENT_VERSION_CHANGED,
    EVENT_DEVICE_STATUS_CHANGED,
    EVENT_ALERT_TRIGGERED,
    EVENT_COMMAND_STATUS_UPDATED,
    EVENT_CONFIGURATION_UPDATED
)

logger = logging.getLogger(__name__)

class RealtimeService:
    """Manages Redis Pub/Sub broadcasting and Socket.IO real-time client emissions."""

    CHANNEL_PORTAL_EVENTS = "channel:portal:events"
    CHANNEL_AGENT_COMMANDS = "channel:agent:commands"

    @classmethod
    def emit_to_company(cls, company_id: str, event_type: str, data: dict, device_id: str = None):
        """Emit standardized real-time event to company room and publish to Redis pub/sub."""
        now_iso = datetime.now(timezone.utc).isoformat()
        payload = {
            "type": event_type,
            "device_id": device_id or data.get("device_id") or data.get("device_uuid") or "",
            "timestamp": now_iso,
            "company_id": company_id,
            "data": data,
            "payload": data
        }

        # 1. Publish to Redis channel for multi-instance scaling
        try:
            redis_client.publish(cls.CHANNEL_PORTAL_EVENTS, json.dumps(payload))
        except Exception as e:
            logger.debug(f"Redis publish error: {e}")

        # 2. Emit directly through local SocketIO to connected web clients
        try:
            socketio.emit(event_type, payload, room=f"company:{company_id}")
            socketio.emit(event_type, payload, room="authenticated_users")
            # Also emit general device status changed listener
            if event_type in [EVENT_DEVICE_REGISTERED, EVENT_DEVICE_ONLINE, EVENT_DEVICE_OFFLINE, EVENT_DEVICE_STALE]:
                socketio.emit(EVENT_DEVICE_STATUS_CHANGED, payload, room=f"company:{company_id}")
                socketio.emit(EVENT_DEVICE_STATUS_CHANGED, payload, room="authenticated_users")
        except Exception as e:
            logger.debug(f"SocketIO emit error: {e}")

        return payload

    @classmethod
    def broadcast_device_registered(cls, company_id: str, device_id: str, hostname: str, payload: dict = None):
        data = {
            "device_id": device_id,
            "hostname": hostname,
            "status": "REGISTERED",
            **(payload or {})
        }
        return cls.emit_to_company(company_id=company_id, event_type=EVENT_DEVICE_REGISTERED, data=data, device_id=device_id)

    @classmethod
    def broadcast_device_online(cls, company_id: str, device_id: str, hostname: str, payload: dict = None):
        data = {
            "device_id": device_id,
            "hostname": hostname,
            "status": "ONLINE",
            **(payload or {})
        }
        return cls.emit_to_company(company_id=company_id, event_type=EVENT_DEVICE_ONLINE, data=data, device_id=device_id)

    @classmethod
    def broadcast_device_offline(cls, company_id: str, device_id: str, hostname: str, payload: dict = None):
        data = {
            "device_id": device_id,
            "hostname": hostname,
            "status": "OFFLINE",
            **(payload or {})
        }
        return cls.emit_to_company(company_id=company_id, event_type=EVENT_DEVICE_OFFLINE, data=data, device_id=device_id)

    @classmethod
    def broadcast_device_stale(cls, company_id: str, device_id: str, hostname: str, payload: dict = None):
        data = {
            "device_id": device_id,
            "hostname": hostname,
            "status": "STALE",
            **(payload or {})
        }
        return cls.emit_to_company(company_id=company_id, event_type=EVENT_DEVICE_STALE, data=data, device_id=device_id)

    @classmethod
    def broadcast_heartbeat_received(cls, company_id: str, device_id: str, hostname: str, payload: dict = None):
        data = {
            "device_id": device_id,
            "hostname": hostname,
            "status": "ONLINE",
            **(payload or {})
        }
        return cls.emit_to_company(company_id=company_id, event_type=EVENT_HEARTBEAT_RECEIVED, data=data, device_id=device_id)

    @classmethod
    def broadcast_agent_version_changed(cls, company_id: str, device_id: str, old_version: str, new_version: str, hostname: str = None):
        data = {
            "device_id": device_id,
            "hostname": hostname or "",
            "old_version": old_version,
            "new_version": new_version
        }
        return cls.emit_to_company(company_id=company_id, event_type=EVENT_AGENT_VERSION_CHANGED, data=data, device_id=device_id)

    @classmethod
    def broadcast_device_status(cls, company_id: str, device_id: str, employee_id: str, status: str, metadata: dict = None):
        """Broadcast DEVICE_STATUS_CHANGED event."""
        return cls.emit_to_company(
            company_id=company_id,
            event_type=EVENT_DEVICE_STATUS_CHANGED,
            data={
                "device_id": device_id,
                "employee_id": employee_id,
                "status": status,
                "metadata": metadata or {}
            },
            device_id=device_id
        )

    @classmethod
    def broadcast_alert(cls, company_id: str, alert_data: dict):
        """Broadcast ALERT_TRIGGERED event."""
        return cls.emit_to_company(
            company_id=company_id,
            event_type=EVENT_ALERT_TRIGGERED,
            data=alert_data
        )

    @classmethod
    def broadcast_command_update(cls, company_id: str, command_data: dict):
        """Broadcast COMMAND_STATUS_UPDATED event."""
        return cls.emit_to_company(
            company_id=company_id,
            event_type=EVENT_COMMAND_STATUS_UPDATED,
            data=command_data
        )
