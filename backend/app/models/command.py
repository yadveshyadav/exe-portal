from app.extensions import db
from app.models.base import BaseModel, get_utc_now

class Command(BaseModel):
    """Safe administrative command queued for delivery to agent."""
    __tablename__ = "commands"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = db.Column(db.String(36), db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)

    command_type = db.Column(db.String(50), nullable=False, index=True) 
    # Safe commands only: 'SYNC', 'REFRESH_CONFIGURATION', 'HEALTH_CHECK', 'CHECK_VERSION'
    parameters = db.Column(db.JSON, default=dict, nullable=False)
    status = db.Column(db.String(30), default="PENDING", nullable=False, index=True)
    # PENDING, SENT, DELIVERED, EXECUTED, FAILED, TIMED_OUT

    created_by = db.Column(db.String(36), nullable=True) # user_id
    sent_at = db.Column(db.DateTime(timezone=True), nullable=True)
    executed_at = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    device = db.relationship("Device", back_populates="commands")
    result = db.relationship("CommandResult", back_populates="command", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        d = super().to_dict()
        d["hostname"] = self.device.hostname if self.device else "Unknown"
        d["result"] = self.result.to_dict() if self.result else None
        return d

    def __repr__(self):
        return f"<Command {self.command_type} for Device {self.device_id} ({self.status})>"


class CommandResult(BaseModel):
    """Execution telemetry result reported back by Windows agent."""
    __tablename__ = "command_results"

    command_id = db.Column(db.String(36), db.ForeignKey("commands.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    device_id = db.Column(db.String(36), db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    
    exit_code = db.Column(db.Integer, default=0, nullable=False)
    result_payload = db.Column(db.JSON, default=dict, nullable=False)
    error_message = db.Column(db.Text, nullable=True)
    reported_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, nullable=False)

    # Relationships
    command = db.relationship("Command", back_populates="result")

    def __repr__(self):
        return f"<CommandResult {self.command_id} Code {self.exit_code}>"
