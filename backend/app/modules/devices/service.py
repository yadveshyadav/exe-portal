import logging
from datetime import datetime, timezone
from app.extensions import db
from app.models.device import Device
from app.models.employee import Employee
from app.models.audit_log import AuditLog
from app.services.presence_service import PresenceService
from app.services.realtime_service import RealtimeService
from app.services.audit_service import AuditService
from app.websocket.connection_manager import connection_manager

logger = logging.getLogger(__name__)

class DeviceService:
    @staticmethod
    def sync_offline_devices(company_id: str, timeout_seconds: int = 60):
        """Finds any device whose last_seen exceeded heartbeat timeout and syncs state."""
        devices = Device.query.filter_by(company_id=company_id, is_active=True).all()
        db_dirty = False
        for dev in devices:
            eff = dev.get_effective_status(timeout_seconds)
            if eff == "OFFLINE" and dev.status not in ["OFFLINE", "DISABLED", "ERROR"]:
                dev.status = "OFFLINE"
                db_dirty = True
                PresenceService.set_device_offline(dev.device_uuid, dev.id)
            elif eff == "STALE" and dev.status not in ["STALE", "OFFLINE", "DISABLED", "ERROR"]:
                dev.status = "STALE"
                db_dirty = True
                PresenceService.set_device_stale(dev.device_uuid, dev.id)
        if db_dirty:
            db.session.commit()

    @staticmethod
    def get_devices_query(
        company_id: str,
        status: str = None,
        search: str = None,
        unassigned: bool = False,
        employee_id: str = None,
        department_id: str = None,
        agent_version: str = None
    ):
        DeviceService.sync_offline_devices(company_id)

        query = Device.query.filter_by(company_id=company_id, is_active=True)

        if search:
            search_fmt = f"%{search}%"
            query = query.outerjoin(Employee, Device.employee_id == Employee.id).filter(
                (Device.hostname.ilike(search_fmt)) |
                (Device.device_uuid.ilike(search_fmt)) |
                (Device.last_ip.ilike(search_fmt)) |
                (Employee.first_name.ilike(search_fmt)) |
                (Employee.last_name.ilike(search_fmt))
            )

        if employee_id:
            query = query.filter(Device.employee_id == employee_id)

        if department_id:
            query = query.join(Employee, Device.employee_id == Employee.id).filter(
                Employee.department_id == department_id
            )

        if agent_version:
            query = query.filter(Device.agent_version == agent_version)

        if unassigned or (status and status.upper() == "UNASSIGNED"):
            query = query.filter(Device.employee_id.is_(None))
        elif status and status.upper() not in ["ALL", ""]:
            norm_status = status.upper()
            if norm_status == "AGENT_ISSUES":
                query = query.filter(
                    (Device.status.in_(["ERROR", "STALE"])) |
                    (Device.last_seen_at.is_(None))
                )
            else:
                query = query.filter(Device.status == norm_status)

        return query.order_by(Device.last_seen_at.desc().nullslast(), Device.registered_at.desc())

    @staticmethod
    def get_device_detail(company_id: str, device_id: str):
        device = Device.query.filter(
            (Device.id == device_id) | (Device.device_uuid == device_id),
            Device.company_id == company_id,
            Device.is_active == True
        ).first()

        if not device:
            return None

        eff = device.get_effective_status()
        if eff != device.status and device.status not in ["DISABLED", "ERROR"]:
            device.status = eff
            db.session.commit()

        detail = device.to_dict()
        detail["agent"] = device.agent.to_dict() if device.agent else None
        detail["employee"] = device.employee.to_dict() if device.employee else None
        
        # Add live Redis state
        redis_state = PresenceService.get_device_presence(device.device_uuid)
        detail["live_state"] = redis_state

        # WebSocket connection status
        agent_sids = connection_manager.get_agent_sids(device.device_uuid)
        detail["websocket_status"] = "CONNECTED" if agent_sids else "DISCONNECTED"

        # Events & Sessions
        detail["recent_events"] = [e.to_dict() for e in device.events[:15]]
        detail["recent_sessions"] = [s.to_dict() for s in device.work_sessions[:10]]

        # Audit History
        logs = AuditLog.query.filter(
            AuditLog.company_id == company_id,
            AuditLog.resource_id == device.id
        ).order_by(AuditLog.created_at.desc()).limit(15).all()
        detail["audit_history"] = [l.to_dict() for l in logs]

        return detail

    @staticmethod
    def update_device(company_id: str, device_id: str, data: dict):
        device = Device.query.filter(
            (Device.id == device_id) | (Device.device_uuid == device_id),
            Device.company_id == company_id,
            Device.is_active == True
        ).first()

        if not device:
            return None, "Device not found"

        before = device.to_dict()

        if "hostname" in data and data["hostname"]:
            device.hostname = data["hostname"]

        if "employee_id" in data:
            old_emp_id = device.employee_id
            new_emp_id = data["employee_id"] if data["employee_id"] else None
            device.employee_id = new_emp_id

            if old_emp_id != new_emp_id:
                action = "EMPLOYEE_ASSIGNED" if new_emp_id else "EMPLOYEE_UNASSIGNED"
                AuditService.log_action(
                    action=action,
                    resource_type="device",
                    resource_id=device.id,
                    before_value={"employee_id": old_emp_id},
                    after_value={"employee_id": new_emp_id},
                    company_id=company_id
                )

        if "status" in data and data["status"]:
            device.status = data["status"]

        db.session.commit()

        # Update Redis presence
        PresenceService.update_device_presence(
            device_id=device.device_uuid,
            status=device.status,
            hostname=device.hostname,
            agent_version=device.agent_version,
            ip_address=device.last_ip,
            employee_id=device.employee_id,
            db_id=device.id
        )

        RealtimeService.broadcast_device_status(
            company_id=company_id,
            device_id=device.device_uuid,
            employee_id=device.employee_id,
            status=device.status,
            metadata={"hostname": device.hostname}
        )

        return device, None

    @staticmethod
    def assign_employee(company_id: str, device_id: str, employee_id: str = None):
        """Assign or unassign employee from device."""
        device = Device.query.filter(
            (Device.id == device_id) | (Device.device_uuid == device_id),
            Device.company_id == company_id,
            Device.is_active == True
        ).first()

        if not device:
            return None, "Device not found"

        old_employee_id = device.employee_id

        if employee_id:
            employee = Employee.query.filter_by(id=employee_id, company_id=company_id, is_active=True).first()
            if not employee:
                return None, "Employee not found"
            device.employee_id = employee.id
            action = "EMPLOYEE_ASSIGNED"
        else:
            device.employee_id = None
            action = "EMPLOYEE_UNASSIGNED"

        db.session.commit()

        AuditService.log_action(
            action=action,
            resource_type="device",
            resource_id=device.id,
            before_value={"employee_id": old_employee_id},
            after_value={"employee_id": device.employee_id},
            company_id=company_id
        )

        PresenceService.update_device_presence(
            device_id=device.device_uuid,
            status=device.status,
            hostname=device.hostname,
            agent_version=device.agent_version,
            ip_address=device.last_ip,
            employee_id=device.employee_id,
            db_id=device.id
        )

        RealtimeService.broadcast_device_status(
            company_id=company_id,
            device_id=device.device_uuid,
            employee_id=device.employee_id,
            status=device.status,
            metadata={"hostname": device.hostname, "action": action}
        )

        return device, None

    @staticmethod
    def disable_device(company_id: str, device_id: str):
        """Administratively disable a device."""
        device = Device.query.filter(
            (Device.id == device_id) | (Device.device_uuid == device_id),
            Device.company_id == company_id,
            Device.is_active == True
        ).first()

        if not device:
            return None, "Device not found"

        device.status = "DISABLED"
        db.session.commit()

        PresenceService.set_device_offline(device.device_uuid, device.id)

        AuditService.log_action(
            action="DEVICE_DISABLED",
            resource_type="device",
            resource_id=device.id,
            company_id=company_id
        )

        RealtimeService.broadcast_device_offline(
            company_id=company_id,
            device_id=device.device_uuid,
            hostname=device.hostname,
            payload={"status": "DISABLED"}
        )

        return device, None

    @staticmethod
    def enable_device(company_id: str, device_id: str):
        """Re-enable a disabled device."""
        device = Device.query.filter(
            (Device.id == device_id) | (Device.device_uuid == device_id),
            Device.company_id == company_id,
            Device.is_active == True
        ).first()

        if not device:
            return None, "Device not found"

        device.status = "REGISTERED"
        db.session.commit()

        AuditService.log_action(
            action="DEVICE_ENABLED",
            resource_type="device",
            resource_id=device.id,
            company_id=company_id
        )

        RealtimeService.broadcast_device_status(
            company_id=company_id,
            device_id=device.device_uuid,
            employee_id=device.employee_id,
            status="REGISTERED",
            metadata={"hostname": device.hostname}
        )

        return device, None

    @staticmethod
    def delete_device(company_id: str, device_id: str):
        device = Device.query.filter(
            (Device.id == device_id) | (Device.device_uuid == device_id),
            Device.company_id == company_id,
            Device.is_active == True
        ).first()

        if not device:
            return False, "Device not found"

        device.is_active = False
        PresenceService.set_device_offline(device.device_uuid, device.id)
        db.session.commit()
        return True, None
