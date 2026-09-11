from app.extensions import db
from app.models.base import BaseModel, get_utc_now

class Event(BaseModel):
    """Immutable device and agent telemetry event log."""
    __tablename__ = "events"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = db.Column(db.String(36), db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)
    
    event_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: AGENT_STARTED, AGENT_STOPPED, HEARTBEAT, ONLINE, OFFLINE, ACTIVE, IDLE, LOCK, UNLOCK, LOGIN, LOGOUT, NETWORK_CONNECTED, NETWORK_DISCONNECTED
    
    event_timestamp = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    received_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    severity = db.Column(db.String(20), default="INFO", nullable=False) # INFO, WARNING, ERROR, CRITICAL
    metadata_payload = db.Column(db.JSON, default=dict, nullable=False)

    # Relationships
    device = db.relationship("Device", back_populates="events")
    employee = db.relationship("Employee", back_populates="events")

    def to_dict(self):
        d = super().to_dict()
        d["hostname"] = self.device.hostname if self.device else "Unknown"
        d["employee_name"] = self.employee.full_name if self.employee else "Unassigned"
        return d

    def __repr__(self):
        return f"<Event {self.event_type} on Device {self.device_id}>"
