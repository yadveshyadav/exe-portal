from datetime import datetime, timezone, timedelta
from app.extensions import db
from app.models.employee import Employee
from app.models.device import Device
from app.models.event import Event
from app.services.presence_service import PresenceService

class DashboardService:
    """Aggregates high-level metrics, live device states, and recent event feeds."""

    @staticmethod
    def get_summary(company_id: str):
        total_employees = Employee.query.filter_by(company_id=company_id, is_active=True).count()
        total_devices = Device.query.filter_by(company_id=company_id, is_active=True).count()
        
        # Calculate real-time counts
        online_count = 0
        offline_count = 0
        stale_count = 0
        unassigned_count = 0
        agent_errors_count = 0
        registered_count = 0
        active_count = 0
        idle_count = 0
        locked_count = 0

        # Query all active devices for this company
        company_devices = Device.query.filter_by(company_id=company_id, is_active=True).all()
        now = datetime.now(timezone.utc)
        db_dirty = False

        for dev in company_devices:
            if dev.employee_id is None:
                unassigned_count += 1

            if dev.status == "ERROR":
                agent_errors_count += 1

            eff_status = dev.get_effective_status(timeout_seconds=60)
            
            # Sync transitions if needed
            if eff_status == "OFFLINE" and dev.status not in ["OFFLINE", "DISABLED", "ERROR"]:
                dev.status = "OFFLINE"
                db_dirty = True
                PresenceService.set_device_offline(dev.device_uuid, dev.id)
            elif eff_status == "STALE" and dev.status not in ["STALE", "OFFLINE", "DISABLED", "ERROR"]:
                dev.status = "STALE"
                db_dirty = True
                PresenceService.set_device_stale(dev.device_uuid, dev.id)

            if eff_status in ["ONLINE", "ACTIVE"]:
                online_count += 1
                active_count += 1
            elif eff_status == "IDLE":
                online_count += 1
                idle_count += 1
            elif eff_status == "LOCKED":
                online_count += 1
                locked_count += 1
            elif eff_status == "STALE":
                stale_count += 1
            elif eff_status == "REGISTERED":
                registered_count += 1
            elif eff_status == "OFFLINE":
                offline_count += 1
            elif eff_status == "ERROR":
                offline_count += 1
        
        if db_dirty:
            db.session.commit()

        return {
            "total_employees": total_employees,
            "total_devices": total_devices,
            "online_devices": online_count,
            "offline_devices": offline_count,
            "stale_devices": stale_count,
            "unassigned_devices": unassigned_count,
            "agent_errors": agent_errors_count,
            "registered_devices": registered_count,
            "active_devices": active_count,
            "idle_devices": idle_count,
            "locked_devices": locked_count,
            "active_alerts": 0,
            "live_workforce_breakdown": {
                "active": active_count,
                "idle": idle_count,
                "offline": offline_count,
                "locked": locked_count,
                "stale": stale_count
            }
        }

    @staticmethod
    def get_recent_events(company_id: str, limit=10):
        events = Event.query.filter_by(company_id=company_id)\
            .order_by(Event.received_at.desc())\
            .limit(limit).all()
        return [e.to_dict() for e in events]
