import time
import threading
import logging
from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models.device import Device
from app.models.agent import Agent
from app.models.event import Event
from app.services.presence_service import PresenceService
from app.services.realtime_service import RealtimeService
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

class HeartbeatService:
    """Processes incoming agent heartbeats, version changes, and watchdog transitions."""

    @classmethod
    def process_heartbeat(
        cls,
        device_uid: str,
        hostname: str = None,
        company_id: str = None,
        agent_version: str = "1.0.0",
        status: str = "ONLINE",
        ip_address: str = None,
        mac_address: str = None,
        os_version: str = None,
        metadata: dict = None
    ):
        now = datetime.now(timezone.utc)
        metadata = metadata or {}

        # 1. Lookup Device by device_uuid (or id)
        device = Device.query.filter(
            (Device.device_uuid == device_uid) | (Device.id == device_uid)
        ).first()

        if not device and company_id:
            # Auto-register if device is heartbeating for the first time
            try:
                device = Device(
                    company_id=company_id,
                    device_uuid=device_uid,
                    hostname=hostname or "Unknown-Workstation",
                    status="ONLINE",
                    operating_system=os_version or "Windows 11",
                    agent_version=agent_version or "1.0.0",
                    last_ip=ip_address,
                    mac_address=mac_address,
                    last_seen_at=now,
                    registered_at=now,
                    is_enrolled=True
                )
                db.session.add(device)
                db.session.flush()
            except Exception:
                db.session.rollback()
                device = Device.query.filter(
                    (Device.device_uuid == device_uid) | (Device.id == device_uid)
                ).first()

        if not device:
            raise ValueError(f"Device with UID {device_uid} not found. Please register first.")

        if device.status == "DISABLED":
            raise PermissionError("Device has been disabled by an administrator.")

        # Check for agent version update
        old_version = device.agent_version or "1.0.0"
        if agent_version and agent_version != old_version:
            device.agent_version = agent_version
            if device.agent:
                device.agent.version = agent_version
            AuditService.log_action(
                action="AGENT_VERSION_CHANGED",
                resource_type="device",
                resource_id=device.id,
                before_value={"agent_version": old_version},
                after_value={"agent_version": agent_version},
                company_id=device.company_id
            )
            RealtimeService.broadcast_agent_version_changed(
                company_id=device.company_id,
                device_id=device.device_uuid,
                old_version=old_version,
                new_version=agent_version,
                hostname=device.hostname
            )

        old_status = device.status
        device.status = status or "ONLINE"
        device.last_seen_at = now
        if ip_address:
            device.last_ip = ip_address
        if hostname:
            device.hostname = hostname
        if os_version:
            device.operating_system = os_version
        if mac_address:
            device.mac_address = mac_address

        # Extract location telemetry if sent in metadata
        loc_data = metadata.get("location") if isinstance(metadata.get("location"), dict) else {}
        if loc_data:
            if loc_data.get("city"):
                device.city = loc_data.get("city")
            if loc_data.get("region") or loc_data.get("state"):
                device.region = loc_data.get("region") or loc_data.get("state")
            if loc_data.get("country"):
                device.country = loc_data.get("country")
            if loc_data.get("latitude") or loc_data.get("lat"):
                try:
                    device.latitude = float(loc_data.get("latitude") or loc_data.get("lat"))
                except (ValueError, TypeError):
                    pass
            if loc_data.get("longitude") or loc_data.get("lon") or loc_data.get("lng"):
                try:
                    device.longitude = float(loc_data.get("longitude") or loc_data.get("lon") or loc_data.get("lng"))
                except (ValueError, TypeError):
                    pass
            if loc_data.get("timezone"):
                device.timezone = loc_data.get("timezone")
            if loc_data.get("isp"):
                device.isp = loc_data.get("isp")

        # 2. Update or create Agent record
        if not device.agent:
            agent = Agent(
                device_id=device.id,
                version=agent_version or "1.0.0",
                last_heartbeat=now,
                agent_status="RUNNING"
            )
            db.session.add(agent)
        else:
            device.agent.version = agent_version or device.agent.version
            device.agent.last_heartbeat = now
            device.agent.agent_status = "RUNNING"

        # Record event in PostgreSQL ONLY if status transitioned from OFFLINE / STALE / REGISTERED
        if old_status in ["OFFLINE", "STALE", "REGISTERED"] and device.status in ["ONLINE", "ACTIVE"]:
            event = Event(
                company_id=device.company_id,
                device_id=device.id,
                employee_id=device.employee_id,
                event_type="ONLINE",
                event_timestamp=now,
                severity="INFO",
                metadata_payload={"hostname": device.hostname, "ip_address": ip_address}
            )
            db.session.add(event)

        db.session.commit()

        # Update work session duration if employee is assigned
        if device.employee_id and status in ["ACTIVE", "IDLE"]:
            try:
                from app.services.session_service import SessionService
                SessionService.start_or_update_session(
                    company_id=device.company_id,
                    employee_id=device.employee_id,
                    device_id=device.id,
                    session_state=status,
                    duration_increment_seconds=30
                )
            except Exception as e:
                logger.debug(f"Session service update error: {e}")

        # 3. Update Fast Redis Live State
        PresenceService.update_device_presence(
            device_id=device.device_uuid,
            status=device.status,
            hostname=device.hostname,
            agent_version=device.agent_version,
            ip_address=device.last_ip,
            employee_id=device.employee_id,
            work_state=status,
            db_id=device.id,
            ttl_seconds=120
        )

        # 4. Publish WebSocket Event
        RealtimeService.broadcast_device_online(
            company_id=device.company_id,
            device_id=device.device_uuid,
            hostname=device.hostname,
            payload={
                "id": device.id,
                "device_id": device.device_uuid,
                "status": device.status,
                "employee_id": device.employee_id,
                "agent_version": device.agent_version,
                "last_seen": now.isoformat()
            }
        )

        return device

    @classmethod
    def check_and_expire_stale_devices(cls, app, timeout_seconds=60):
        """Scans devices and marks missing heartbeats as STALE or OFFLINE."""
        with app.app_context():
            now = datetime.now(timezone.utc)
            stale_threshold = now - timedelta(seconds=timeout_seconds)
            offline_threshold = now - timedelta(seconds=timeout_seconds * 2)

            # Active non-disabled devices
            active_devices = Device.query.filter(
                Device.is_active == True,
                Device.status.notin_(["DISABLED", "ERROR"])
            ).all()

            db_dirty = False
            for dev in active_devices:
                if not dev.last_seen_at:
                    continue

                last_seen_tz = dev.last_seen_at if dev.last_seen_at.tzinfo else dev.last_seen_at.replace(tzinfo=timezone.utc)

                if last_seen_tz < offline_threshold and dev.status != "OFFLINE":
                    logger.info(f"Watchdog: Device {dev.hostname} ({dev.device_uuid}) offline threshold exceeded. Marking OFFLINE.")
                    dev.status = "OFFLINE"
                    db_dirty = True
                    PresenceService.set_device_offline(dev.device_uuid, dev.id)

                    offline_event = Event(
                        company_id=dev.company_id,
                        device_id=dev.id,
                        employee_id=dev.employee_id,
                        event_type="OFFLINE",
                        event_timestamp=now,
                        severity="WARNING",
                        metadata_payload={"reason": "Heartbeat timeout"}
                    )
                    db.session.add(offline_event)

                    RealtimeService.broadcast_device_offline(
                        company_id=dev.company_id,
                        device_id=dev.device_uuid,
                        hostname=dev.hostname,
                        payload={"status": "OFFLINE", "id": dev.id}
                    )

                elif last_seen_tz < stale_threshold and last_seen_tz >= offline_threshold and dev.status not in ["STALE", "OFFLINE"]:
                    logger.info(f"Watchdog: Device {dev.hostname} ({dev.device_uuid}) stale threshold exceeded. Marking STALE.")
                    dev.status = "STALE"
                    db_dirty = True
                    PresenceService.set_device_stale(dev.device_uuid, dev.id)

                    RealtimeService.broadcast_device_stale(
                        company_id=dev.company_id,
                        device_id=dev.device_uuid,
                        hostname=dev.hostname,
                        payload={"status": "STALE", "id": dev.id}
                    )

            if db_dirty:
                db.session.commit()

def start_heartbeat_watchdog(app, interval_seconds=10, timeout_seconds=60):
    """Starts background daemon thread to monitor and expire offline devices."""
    def run_watchdog():
        while True:
            try:
                HeartbeatService.check_and_expire_stale_devices(app, timeout_seconds)
            except Exception as e:
                logger.error(f"Error in heartbeat watchdog: {e}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=run_watchdog, daemon=True)
    thread.start()
    logger.info("[*] Heartbeat Watchdog daemon started (checks every 10s).")
    return thread
