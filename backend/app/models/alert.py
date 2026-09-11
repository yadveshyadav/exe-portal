from app.extensions import db
from app.models.base import BaseModel, get_utc_now

class Alert(BaseModel):
    """System & behavioral threshold alert entity."""
    __tablename__ = "alerts"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = db.Column(db.String(36), db.ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)

    alert_type = db.Column(db.String(50), nullable=False, index=True) # e.g. 'HEARTBEAT_LOST', 'VERSION_MISMATCH', 'IDLE_SPIKE'
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(20), default="MEDIUM", nullable=False, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    status = db.Column(db.String(30), default="TRIGGERED", nullable=False, index=True) # TRIGGERED, ACKNOWLEDGED, RESOLVED, DISMISSED
    
    triggered_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    resolved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    resolved_by = db.Column(db.String(36), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)

    # Relationships
    device = db.relationship("Device", back_populates="alerts")
    employee = db.relationship("Employee", back_populates="alerts")

    def to_dict(self):
        d = super().to_dict()
        d["hostname"] = self.device.hostname if self.device else "N/A"
        d["employee_name"] = self.employee.full_name if self.employee else "Unassigned"
        return d

    def __repr__(self):
        return f"<Alert {self.severity} - {self.title}>"
