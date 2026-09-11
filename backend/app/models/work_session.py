from app.extensions import db
from app.models.base import BaseModel

class WorkSession(BaseModel):
    """Calculated work and activity duration session."""
    __tablename__ = "work_sessions"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = db.Column(db.String(36), db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)

    session_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    end_time = db.Column(db.DateTime(timezone=True), nullable=True)
    
    total_duration_seconds = db.Column(db.Integer, default=0, nullable=False)
    active_duration_seconds = db.Column(db.Integer, default=0, nullable=False)
    idle_duration_seconds = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(30), default="OPEN", nullable=False) # OPEN, CLOSED

    # Relationships
    employee = db.relationship("Employee", back_populates="work_sessions")
    device = db.relationship("Device", back_populates="work_sessions")

    def to_dict(self):
        d = super().to_dict()
        d["employee_name"] = self.employee.full_name if self.employee else "Unknown"
        d["employee_code"] = self.employee.employee_code if self.employee else None
        d["hostname"] = self.device.hostname if self.device else "Unknown"
        d["current_state"] = self.device.get_effective_status() if self.device else "OFFLINE"
        d["session_date"] = self.session_date.isoformat() if self.session_date else None
        d["start_time"] = self.start_time.isoformat() if self.start_time else None
        d["end_time"] = self.end_time.isoformat() if self.end_time else None

        if self.start_time and self.end_time:
            diff = (self.end_time - self.start_time).total_seconds()
            d["calculated_duration_seconds"] = max(int(diff), self.total_duration_seconds)
        else:
            d["calculated_duration_seconds"] = self.total_duration_seconds
        return d

    def __repr__(self):
        return f"<WorkSession {self.session_date} for Emp {self.employee_id} ({self.status})>"
