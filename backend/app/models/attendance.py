from app.extensions import db
from app.models.base import BaseModel

class Attendance(BaseModel):
    """Daily aggregated attendance record."""
    __tablename__ = "attendance_records"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    
    attendance_date = db.Column(db.Date, nullable=False, index=True)
    first_check_in = db.Column(db.DateTime(timezone=True), nullable=True)
    last_check_out = db.Column(db.DateTime(timezone=True), nullable=True)
    total_work_seconds = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.String(30), default="PRESENT", nullable=False) # PRESENT, ABSENT, HALF_DAY, ON_LEAVE
    verification_status = db.Column(db.String(30), default="VERIFIED", nullable=False) # VERIFIED, PENDING_REVIEW, MANUAL_OVERRIDE

    # Relationships
    employee = db.relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        db.UniqueConstraint("company_id", "employee_id", "attendance_date", name="uq_employee_attendance_date"),
    )

    def to_dict(self):
        d = super().to_dict()
        d["employee_name"] = self.employee.full_name if self.employee else "Unknown"
        d["employee_code"] = self.employee.employee_code if self.employee else None
        d["department_name"] = self.employee.department.name if self.employee and self.employee.department else None

        primary_device = self.employee.devices[0] if (self.employee and self.employee.devices) else None
        if primary_device:
            d["device_id"] = primary_device.id
            d["hostname"] = primary_device.hostname
            d["current_state"] = primary_device.get_effective_status()
            d["os_name"] = primary_device.os_name
        else:
            d["device_id"] = None
            d["hostname"] = "Unassigned"
            d["current_state"] = "OFFLINE"
            d["os_name"] = "Windows"

        d["attendance_date"] = self.attendance_date.isoformat() if self.attendance_date else None
        d["first_check_in"] = self.first_check_in.isoformat() if self.first_check_in else None
        d["last_check_out"] = self.last_check_out.isoformat() if self.last_check_out else None

        if self.first_check_in and self.last_check_out:
            diff = (self.last_check_out - self.first_check_in).total_seconds()
            d["calculated_duration_seconds"] = max(int(diff), self.total_work_seconds)
        else:
            d["calculated_duration_seconds"] = self.total_work_seconds

        return d

    def __repr__(self):
        return f"<Attendance {self.attendance_date} - Emp {self.employee_id}>"
