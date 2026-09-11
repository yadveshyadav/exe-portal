from app.extensions import db
from app.models.base import BaseModel

class Agent(BaseModel):
    """emp_runexe Windows Agent installed instance."""
    __tablename__ = "agents"

    device_id = db.Column(db.String(36), db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    version = db.Column(db.String(50), default="1.0.0", nullable=False)
    build_number = db.Column(db.String(50), nullable=True)
    agent_status = db.Column(db.String(30), default="RUNNING", nullable=False) # RUNNING, STOPPED, ERROR, OUTDATED
    last_heartbeat = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    config_version = db.Column(db.String(50), default="1.0", nullable=False)
    config_hash = db.Column(db.String(64), nullable=True)
    binary_hash = db.Column(db.String(64), nullable=True)

    # Relationships
    device = db.relationship("Device", back_populates="agent")

    def __repr__(self):
        return f"<Agent v{self.version} for Device {self.device_id}>"
