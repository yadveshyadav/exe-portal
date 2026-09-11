from datetime import datetime, timezone
from app.extensions import db
from app.models.alert import Alert
from app.services.realtime_service import RealtimeService

class AlertService:
    """Manages creation, acknowledgment, and resolution of threshold alerts."""

    @classmethod
    def trigger_alert(
        cls,
        company_id: str,
        alert_type: str,
        title: str,
        description: str,
        severity: str = "MEDIUM",
        device_id: str = None,
        employee_id: str = None
    ):
        now = datetime.now(timezone.utc)
        alert = Alert(
            company_id=company_id,
            device_id=device_id,
            employee_id=employee_id,
            alert_type=alert_type,
            title=title,
            description=description,
            severity=severity,
            status="TRIGGERED",
            triggered_at=now
        )
        db.session.add(alert)
        db.session.commit()

        # Broadcast over real-time bus
        RealtimeService.broadcast_alert(company_id, alert.to_dict())
        return alert

    @classmethod
    def resolve_alert(cls, alert_id: str, user_id: str, notes: str = None):
        alert = Alert.query.get(alert_id)
        if not alert:
            return None

        alert.status = "RESOLVED"
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolved_by = user_id
        alert.resolution_notes = notes
        db.session.commit()
        return alert
