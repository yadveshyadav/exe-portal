from datetime import datetime, timezone, date
from app.extensions import db
from app.models.work_session import WorkSession
from app.models.attendance import Attendance
from app.models.event import Event
from app.models.device import Device
from app.services.presence_service import PresenceService
from app.services.realtime_service import RealtimeService

class SessionService:
    """Manages active work sessions, login/logout transitions, sleep modes, and daily attendance aggregation."""

    @classmethod
    def start_or_update_session(
        cls,
        company_id: str,
        employee_id: str,
        device_id: str,
        session_state: str = "ACTIVE", # ACTIVE or IDLE
        duration_increment_seconds: int = 30
    ):
        now = datetime.now(timezone.utc)
        today = now.date()

        # 1. Look for existing open session for this employee & device today
        session = WorkSession.query.filter_by(
            company_id=company_id,
            employee_id=employee_id,
            device_id=device_id,
            session_date=today,
            status="OPEN"
        ).first()

        if not session:
            session = WorkSession(
                company_id=company_id,
                employee_id=employee_id,
                device_id=device_id,
                session_date=today,
                start_time=now,
                status="OPEN",
                total_duration_seconds=duration_increment_seconds,
                active_duration_seconds=duration_increment_seconds if session_state == "ACTIVE" else 0,
                idle_duration_seconds=duration_increment_seconds if session_state == "IDLE" else 0
            )
            db.session.add(session)
        else:
            session.total_duration_seconds += duration_increment_seconds
            if session_state == "ACTIVE":
                session.active_duration_seconds += duration_increment_seconds
            elif session_state == "IDLE":
                session.idle_duration_seconds += duration_increment_seconds
            session.end_time = now

        # 2. Update Daily Attendance
        attendance = Attendance.query.filter_by(
            company_id=company_id,
            employee_id=employee_id,
            attendance_date=today
        ).first()

        if not attendance:
            attendance = Attendance(
                company_id=company_id,
                employee_id=employee_id,
                attendance_date=today,
                first_check_in=now,
                last_check_out=now,
                total_work_seconds=duration_increment_seconds,
                status="PRESENT"
            )
            db.session.add(attendance)
        else:
            attendance.last_check_out = now
            attendance.total_work_seconds += duration_increment_seconds
            if attendance.total_work_seconds >= 14400: # >= 4 hours
                attendance.status = "PRESENT"
            elif attendance.total_work_seconds >= 3600: # >= 1 hour
                attendance.status = "HALF_DAY"

        db.session.commit()
        return session

    @classmethod
    def record_agent_event(
        cls,
        company_id: str,
        device_id: str,
        event_type: str,
        occurred_at: datetime = None,
        metadata: dict = None
    ):
        """Record lifecycle events: LOGIN, LOGOUT, SLEEP, RESUME, LOCK, UNLOCK."""
        now = occurred_at or datetime.now(timezone.utc)
        today = now.date()

        device = Device.query.filter_by(id=device_id, company_id=company_id).first()
        employee_id = device.employee_id if device else None

        # 1. Store immutable event log
        event = Event(
            company_id=company_id,
            device_id=device_id,
            employee_id=employee_id,
            event_type=event_type,
            event_timestamp=now,
            received_at=datetime.now(timezone.utc),
            severity="INFO",
            metadata_payload=metadata or {}
        )
        db.session.add(event)

        # 2. Process state transitions
        if event_type == "LOGIN" or event_type == "UNLOCK" or event_type == "RESUME":
            if device:
                device.status = "ACTIVE"
                PresenceService.set_device_status(device_id, "ACTIVE")
            if employee_id:
                cls.start_or_update_session(company_id, employee_id, device_id, "ACTIVE", duration_increment_seconds=0)

        elif event_type == "LOGOUT":
            if device:
                device.status = "OFFLINE"
                PresenceService.set_device_status(device_id, "OFFLINE")
            # Close open work session
            if employee_id:
                open_session = WorkSession.query.filter_by(
                    company_id=company_id,
                    employee_id=employee_id,
                    device_id=device_id,
                    session_date=today,
                    status="OPEN"
                ).first()
                if open_session:
                    open_session.status = "CLOSED"
                    open_session.end_time = now

        elif event_type == "SLEEP" or event_type == "SUSPEND":
            if device:
                device.status = "OFFLINE"
                PresenceService.set_device_status(device_id, "OFFLINE")
            # Close/pause open session
            if employee_id:
                open_session = WorkSession.query.filter_by(
                    company_id=company_id,
                    employee_id=employee_id,
                    device_id=device_id,
                    session_date=today,
                    status="OPEN"
                ).first()
                if open_session:
                    open_session.end_time = now

        elif event_type == "LOCK":
            if device:
                device.status = "LOCKED"
                PresenceService.set_device_status(device_id, "LOCKED")

        db.session.commit()

        # Broadcast live status and event to connected portals
        if device:
            RealtimeService.broadcast_device_status(
                company_id=company_id,
                device_id=device.id,
                employee_id=device.employee_id,
                status=device.status,
                metadata={"hostname": device.hostname, "event_type": event_type}
            )

        RealtimeService.emit_to_company(
            company_id=company_id,
            event_type="EVENT_RECORDED",
            data=event.to_dict()
        )

        return event
