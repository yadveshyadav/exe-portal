from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import synonym
from app.extensions import db
from app.models.base import BaseModel, get_utc_now

class Device(BaseModel):
    """Enrolled Windows hardware device managed by emp_runexe."""
    __tablename__ = "devices"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Device Identification
    device_uuid = db.Column(db.String(100), nullable=False, unique=True, index=True)
    hostname = db.Column(db.String(150), nullable=False, index=True)
    operating_system = db.Column(db.String(150), default="Windows 11", nullable=False)
    agent_version = db.Column(db.String(50), default="1.0.0", nullable=False)
    
    # Status: REGISTERED, ONLINE, STALE, OFFLINE, DISABLED, ERROR
    status = db.Column(db.String(30), default="REGISTERED", nullable=False, index=True)
    
    # Network & Diagnostic telemetry
    last_ip = db.Column(db.String(50), nullable=True)
    mac_address = db.Column(db.String(50), nullable=True)
    
    # Geolocation Telemetry
    city = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    timezone = db.Column(db.String(100), nullable=True)
    isp = db.Column(db.String(150), nullable=True)
    
    # Timestamps
    registered_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, nullable=False)
    last_seen_at = db.Column(db.DateTime(timezone=True), nullable=True, index=True)
    
    is_enrolled = db.Column(db.Boolean, default=True, nullable=False)

    # SQLAlchemy Synonyms for complete query & attribute compatibility
    device_uid = synonym("device_uuid")
    device_id = synonym("device_uuid")
    last_seen = synonym("last_seen_at")
    ip_address = synonym("last_ip")
    os_name = synonym("operating_system")

    # Relationships
    company = db.relationship("Company", back_populates="devices")
    employee = db.relationship("Employee", back_populates="devices", foreign_keys=[employee_id])
    agent = db.relationship("Agent", back_populates="device", uselist=False, cascade="all, delete-orphan")
    events = db.relationship("Event", back_populates="device", cascade="all, delete-orphan", order_by="desc(Event.event_timestamp)")
    work_sessions = db.relationship("WorkSession", back_populates="device", cascade="all, delete-orphan", order_by="desc(WorkSession.start_time)")
    alerts = db.relationship("Alert", back_populates="device", cascade="all, delete-orphan")
    commands = db.relationship("Command", back_populates="device", cascade="all, delete-orphan")

    def get_effective_status(self, timeout_seconds=None):
        """Calculates real-time device status combining DB state and heartbeat timeout."""
        if self.status in ["DISABLED", "ERROR"]:
            return self.status

        if not self.last_seen_at:
            return "REGISTERED"

        if timeout_seconds is None:
            try:
                from flask import current_app
                timeout_seconds = current_app.config.get("HEARTBEAT_TIMEOUT_SECONDS", 60)
            except Exception:
                timeout_seconds = 60

        now = datetime.now(timezone.utc)
        last_seen_tz = self.last_seen_at if self.last_seen_at.tzinfo else self.last_seen_at.replace(tzinfo=timezone.utc)
        diff_sec = (now - last_seen_tz).total_seconds()

        if diff_sec > (timeout_seconds * 2):
            return "OFFLINE"
        elif diff_sec > timeout_seconds:
            return "STALE"
        
        if self.status in ["OFFLINE", "REGISTERED"]:
            return "ONLINE"

        return self.status

    def to_dict(self):
        d = super().to_dict()
        d["device_id"] = self.device_uuid
        d["device_uuid"] = self.device_uuid
        d["device_uid"] = self.device_uuid
        d["status"] = self.get_effective_status()
        d["last_seen"] = self.last_seen_at.isoformat() if self.last_seen_at else None
        d["last_seen_at"] = self.last_seen_at.isoformat() if self.last_seen_at else None
        d["last_ip"] = self.last_ip
        d["ip_address"] = self.last_ip
        d["city"] = self.city
        d["region"] = self.region
        d["country"] = self.country
        d["latitude"] = self.latitude
        d["longitude"] = self.longitude
        d["timezone"] = self.timezone
        d["isp"] = self.isp
        # Formatted string helper
        loc_parts = [p for p in [self.city, self.region, self.country] if p]
        d["location_formatted"] = ", ".join(loc_parts) if loc_parts else None
        d["operating_system"] = self.operating_system
        d["os_name"] = self.operating_system
        d["os_version"] = self.operating_system
        d["agent_version"] = self.agent_version or (self.agent.version if self.agent else "1.0.0")
        d["employee_id"] = self.employee_id
        d["employee_name"] = self.employee.full_name if self.employee else "Unassigned"
        d["employee_code"] = self.employee.employee_code if self.employee else None
        d["registered_at"] = self.registered_at.isoformat() if self.registered_at else None
        return d

    def __repr__(self):
        return f"<Device {self.hostname} ({self.device_uuid}) [{self.get_effective_status()}]>"
