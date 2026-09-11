import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import PERM_AGENTS_VIEW, PERM_AGENTS_MANAGE
from app.middleware.authentication import get_current_user
from app.modules.agents.schemas import AgentConfigPushRequest, AgentRegisterRequest, AgentHeartbeatRequest
from app.modules.agents.service import AgentService
from app.services.heartbeat_service import HeartbeatService
from app.services.presence_service import PresenceService
from app.services.realtime_service import RealtimeService
from app.services.session_service import SessionService
from app.services.audit_service import AuditService
from app.models.company import Company
from app.models.device import Device
from app.models.agent import Agent
from app.models.base import get_utc_now
from app.utils.validators import validate_request
from app.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

agents_bp = Blueprint("agents", __name__, url_prefix="/api/v1/agents")

def get_client_ip():
    """Extract real client IP considering trusted proxy headers."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    if request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP").strip()
    return request.remote_addr or "127.0.0.1"

@agents_bp.route("/register", methods=["POST"])
def register_agent():
    """
    Device Registration API for emp_runexe Windows Agent.
    POST /api/v1/agents/register
    """
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id") or data.get("device_uid")
    hostname = data.get("hostname")
    operating_system = data.get("operating_system") or data.get("os_version") or data.get("os_name") or "Windows 11"
    agent_version = data.get("agent_version") or "1.0.0"
    company_code = data.get("company_code")
    company_id = data.get("company_id")
    mac_address = data.get("mac_address")

    if not device_id or not hostname:
        return error_response(
            message="device_id and hostname are required fields",
            errors=["device_id is required", "hostname is required"],
            status_code=400
        )

    # Resolve company
    comp = None
    if company_id:
        comp = Company.query.filter_by(id=company_id).first()
    elif company_code:
        comp = Company.query.filter_by(code=company_code).first()
    if not comp:
        comp = Company.query.first()
    if not comp:
        return error_response(message="No registered company found in portal", status_code=500)

    now = get_utc_now()
    client_ip = get_client_ip()

    # Search existing device by device_uuid or id
    device = Device.query.filter(
        (Device.device_uuid == device_id) | (Device.id == device_id)
    ).first()

    is_new = False
    if not device:
        # Check by hostname & company as fallback before creating new
        is_new = True
        device = Device(
            company_id=comp.id,
            device_uuid=device_id,
            hostname=hostname,
            operating_system=operating_system,
            agent_version=agent_version,
            status="REGISTERED",
            employee_id=None,  # Registration NEVER mandates employee assignment
            last_ip=client_ip,
            mac_address=mac_address,
            registered_at=now,
            last_seen_at=None,
            is_enrolled=True,
            is_active=True
        )
        db.session.add(device)
        db.session.flush()

        agent = Agent(
            device_id=device.id,
            version=agent_version,
            last_heartbeat=now,
            agent_status="RUNNING"
        )
        db.session.add(agent)
    else:
        # Check if device is disabled
        if device.status == "DISABLED":
            return error_response(
                message="Device has been disabled by administrator",
                status_code=403
            )

        # Upsert / Update existing device attributes
        device.hostname = hostname
        device.operating_system = operating_system
        device.agent_version = agent_version
        device.last_ip = client_ip
        if mac_address:
            device.mac_address = mac_address
        device.is_active = True

        # Extract location if sent
        loc_data = data.get("location") or (data.get("metadata", {}).get("location") if isinstance(data.get("metadata"), dict) else {})
        if loc_data:
            if loc_data.get("city"): device.city = loc_data.get("city")
            if loc_data.get("region") or loc_data.get("state"): device.region = loc_data.get("region") or loc_data.get("state")
            if loc_data.get("country"): device.country = loc_data.get("country")
            if loc_data.get("latitude") or loc_data.get("lat"):
                try: device.latitude = float(loc_data.get("latitude") or loc_data.get("lat"))
                except (ValueError, TypeError): pass
            if loc_data.get("longitude") or loc_data.get("lon") or loc_data.get("lng"):
                try: device.longitude = float(loc_data.get("longitude") or loc_data.get("lon") or loc_data.get("lng"))
                except (ValueError, TypeError): pass
            if loc_data.get("timezone"): device.timezone = loc_data.get("timezone")
            if loc_data.get("isp"): device.isp = loc_data.get("isp")

        if not device.agent:
            agent = Agent(
                device_id=device.id,
                version=agent_version,
                last_heartbeat=now,
                agent_status="RUNNING"
            )
            db.session.add(agent)
        else:
            device.agent.version = agent_version

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        device = Device.query.filter(
            (Device.device_uuid == device_id) | (Device.id == device_id)
        ).first()
        if not device:
            logger.error(f"Error registering device {device_id}: {e}")
            return error_response(message="Failed to register device", status_code=500)
        is_new = False

    # Update Redis Presence State
    PresenceService.update_device_presence(
        device_id=device.device_uuid,
        status=device.status,
        hostname=device.hostname,
        agent_version=device.agent_version,
        ip_address=device.last_ip,
        employee_id=device.employee_id,
        db_id=device.id,
        ttl_seconds=120
    )

    # Publish WebSocket Event
    RealtimeService.broadcast_device_registered(
        company_id=comp.id,
        device_id=device.device_uuid,
        hostname=device.hostname,
        payload={
            "id": device.id,
            "device_id": device.device_uuid,
            "hostname": device.hostname,
            "status": device.status,
            "operating_system": device.operating_system,
            "agent_version": device.agent_version,
            "employee_id": device.employee_id,
            "employee_name": "Unassigned"
        }
    )

    # Audit log entry
    AuditService.log_action(
        action="DEVICE_REGISTERED" if is_new else "DEVICE_RECONNECTED",
        resource_type="device",
        resource_id=device.id,
        after_value={
            "device_uuid": device.device_uuid,
            "hostname": device.hostname,
            "ip": client_ip,
            "agent_version": agent_version
        },
        company_id=comp.id
    )

    status_code = 201 if is_new else 200
    return jsonify({
        "success": True,
        "device": {
            "id": device.id,
            "device_id": device.device_uuid,
            "hostname": device.hostname,
            "status": device.status
        }
    }), status_code

@agents_bp.route("/heartbeat", methods=["POST"])
def agent_rest_heartbeat():
    """
    Periodic Heartbeat API for Windows emp_runexe agent.
    POST /api/v1/agents/heartbeat
    """
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id") or data.get("device_uid")
    timestamp = data.get("timestamp")
    agent_version = data.get("agent_version") or "1.0.0"
    status = data.get("status") or "ONLINE"
    hostname = data.get("hostname")
    os_version = data.get("operating_system") or data.get("os_version")
    company_code = data.get("company_code")
    company_id = data.get("company_id")
    mac_address = data.get("mac_address")
    metadata = data.get("metadata") or {}

    if not device_id:
        return error_response(message="device_id (or device_uid) is required", status_code=400)

    # Resolve company if provided
    comp = None
    if company_id:
        comp = Company.query.filter_by(id=company_id).first()
    elif company_code:
        comp = Company.query.filter_by(code=company_code).first()
    if not comp:
        comp = Company.query.first()

    client_ip = get_client_ip()

    try:
        device = HeartbeatService.process_heartbeat(
            device_uid=device_id,
            hostname=hostname,
            company_id=comp.id if comp else None,
            agent_version=agent_version,
            status=status,
            ip_address=client_ip,
            mac_address=mac_address,
            os_version=os_version,
            metadata=metadata
        )

        agent_config = AgentService.get_agent_config(device.company_id, device.id)

        return success_response(
            data={
                "device_id": device.id,
                "device_uuid": device.device_uuid,
                "status": "ACK",
                "registered_status": device.status,
                "config": agent_config
            },
            message="Heartbeat recorded successfully"
        )
    except PermissionError as pe:
        return error_response(message=str(pe), status_code=403)
    except ValueError as ve:
        return error_response(message=str(ve), status_code=404)
    except Exception as e:
        logger.error(f"Heartbeat processing error: {e}", exc_info=True)
        return error_response(message=str(e), status_code=500)

@agents_bp.route("/events", methods=["POST"])
def agent_rest_events():
    """REST Lifecycle Events endpoint for LOGIN, LOGOUT, SLEEP, RESUME, LOCK, UNLOCK."""
    data = request.get_json(silent=True) or {}
    device_uid = data.get("device_id") or data.get("device_uid")
    company_id = data.get("company_id")
    company_code = data.get("company_code")
    event_type = data.get("event_type")

    if not company_id and company_code:
        comp = Company.query.filter_by(code=company_code).first()
        if comp:
            company_id = comp.id
    if not company_id:
        comp = Company.query.first()
        if comp:
            company_id = comp.id

    if not device_uid or not company_id or not event_type:
        return error_response(
            message="device_id, company_id (or company_code), and event_type are required", 
            status_code=400
        )

    device = Device.query.filter(
        (Device.device_uuid == device_uid) | (Device.id == device_uid)
    ).first()

    if not device:
        client_ip = get_client_ip()
        device = HeartbeatService.process_heartbeat(
            device_uid=device_uid,
            hostname=data.get("hostname", "Unknown-Workstation"),
            company_id=company_id,
            status="ACTIVE" if event_type in ["LOGIN", "RESUME", "UNLOCK"] else "OFFLINE",
            ip_address=client_ip
        )

    try:
        event = SessionService.record_agent_event(
            company_id=company_id,
            device_id=device.id,
            event_type=event_type.upper(),
            metadata=data.get("metadata", {})
        )
        return success_response(
            data={"event_id": event.id, "event_type": event.event_type, "status": "RECORDED"},
            message=f"Event {event_type} recorded successfully"
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)

@agents_bp.route("", methods=["GET"])
@require_permission(PERM_AGENTS_VIEW)
def list_agents():
    user = get_current_user()
    agents = AgentService.get_agents_overview(user.company_id)
    return success_response(data={"items": agents})

@agents_bp.route("/config", methods=["GET"])
@require_permission(PERM_AGENTS_VIEW)
def get_global_config():
    user = get_current_user()
    config = AgentService.get_agent_config(user.company_id)
    return success_response(data={"configuration": config})

@agents_bp.route("/config", methods=["POST"])
@require_permission(PERM_AGENTS_MANAGE)
@validate_request(AgentConfigPushRequest)
def push_global_config(validated_data: AgentConfigPushRequest):
    user = get_current_user()
    res, err = AgentService.push_configuration(
        user.company_id,
        "global",
        validated_data.model_dump(exclude_unset=True)
    )
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=res, message="Global configuration updated and dispatched")

@agents_bp.route("/<string:device_id>/config", methods=["GET"])
@require_permission(PERM_AGENTS_VIEW)
def get_device_config(device_id: str):
    user = get_current_user()
    config = AgentService.get_agent_config(user.company_id, device_id)
    return success_response(data={"device_id": device_id, "configuration": config})

@agents_bp.route("/<string:device_id>/config", methods=["POST"])
@require_permission(PERM_AGENTS_MANAGE)
@validate_request(AgentConfigPushRequest)
def push_config(device_id: str, validated_data: AgentConfigPushRequest):
    user = get_current_user()
    res, err = AgentService.push_configuration(
        user.company_id,
        device_id,
        validated_data.model_dump(exclude_unset=True)
    )
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=res, message="Configuration dispatched to agent")
