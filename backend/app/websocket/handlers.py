import logging
from flask import request
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio, db
from app.websocket.connection_manager import connection_manager
from app.websocket.events import (
    EVENT_AGENT_HEARTBEAT,
    EVENT_AGENT_HEARTBEAT_ACK,
    EVENT_AGENT_COMMAND_RESULT,
    EVENT_PORTAL_SUBSCRIBE,
    EVENT_DEVICE_STATUS_CHANGED,
    EVENT_DEVICE_OFFLINE
)
from app.services.heartbeat_service import HeartbeatService
from app.services.command_service import CommandService
from app.services.presence_service import PresenceService
from app.services.session_service import SessionService
from app.services.realtime_service import RealtimeService
from app.models.device import Device

logger = logging.getLogger(__name__)

def register_websocket_handlers(sio):
    """Register all SocketIO lifecycle and telemetry handlers."""

    @sio.on("connect")
    def handle_connect(auth):
        sid = request.sid
        logger.info(f"WebSocket client connected: {sid}")
        emit("connected", {"status": "connected", "sid": sid})

    @sio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        conn_type, details = connection_manager.remove_connection(sid)
        if conn_type == "agent" and details:
            device_id = details.get("device_id")
            company_id = details.get("company_id")
            if device_id and company_id:
                # Mark as OFFLINE in presence cache
                PresenceService.set_device_offline(device_id)
                # Emit OFFLINE event
                RealtimeService.broadcast_device_offline(
                    company_id=company_id,
                    device_id=device_id,
                    hostname=details.get("hostname", "Workstation")
                )

    @sio.on(EVENT_PORTAL_SUBSCRIBE)
    def handle_portal_subscribe(data):
        """Portal frontend joins its company room to receive real-time streams."""
        sid = request.sid
        company_id = data.get("company_id")
        user_id = data.get("user_id")

        if company_id:
            join_room(f"company:{company_id}")
            join_room("authenticated_users")
            connection_manager.register_portal_user(sid, user_id or "anonymous", company_id)
            emit("subscribed", {"status": "success", "company_id": company_id})

    @sio.on(EVENT_AGENT_HEARTBEAT)
    def handle_agent_heartbeat(data):
        """Windows Agent heartbeat over WebSocket."""
        sid = request.sid
        device_uid = data.get("device_id") or data.get("device_uid")
        company_id = data.get("company_id")
        hostname = data.get("hostname", "Unknown-PC")
        status = data.get("status", "ONLINE")
        agent_version = data.get("agent_version", "1.0.0")
        ip_address = data.get("ip_address", request.remote_addr)
        mac_address = data.get("mac_address")
        os_version = data.get("operating_system") or data.get("os_version")
        metadata = data.get("metadata", {})

        if not device_uid or not company_id:
            emit("error", {"message": "device_id/device_uid and company_id required"})
            return

        try:
            device = HeartbeatService.process_heartbeat(
                device_uid=device_uid,
                hostname=hostname,
                company_id=company_id,
                agent_version=agent_version,
                status=status,
                ip_address=ip_address,
                mac_address=mac_address,
                os_version=os_version,
                metadata=metadata
            )

            # Register connection association
            connection_manager.register_agent(sid, device.device_uuid, company_id, device.id)
            join_room(f"device:{device.id}")

            # Acknowledge heartbeat back to agent
            emit(EVENT_AGENT_HEARTBEAT_ACK, {
                "device_id": device.id,
                "device_uuid": device.device_uuid,
                "status": "ACK",
                "server_time": data.get("timestamp")
            })
        except Exception as e:
            logger.error(f"Error handling agent heartbeat: {e}")
            emit("error", {"message": str(e)})

    @sio.on(EVENT_AGENT_COMMAND_RESULT)
    def handle_agent_command_result(data):
        """Windows agent reports result of an executed command."""
        command_id = data.get("command_id")
        device_id = data.get("device_id")
        exit_code = data.get("exit_code", 0)
        result_payload = data.get("result_payload", {})
        error_message = data.get("error_message")

        if command_id and device_id:
            CommandService.record_command_result(
                command_id=command_id,
                device_id=device_id,
                exit_code=exit_code,
                result_payload=result_payload,
                error_message=error_message
            )
            emit("command_result_ack", {"status": "recorded", "command_id": command_id})
