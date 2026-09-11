from app.extensions import db
from app.models.base import BaseModel

class Employee(BaseModel):
    """Employee workforce profile entity."""
    __tablename__ = "employees"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    department_id = db.Column(db.String(36), db.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    employee_code = db.Column(db.String(50), nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(50), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(30), default="ACTIVE", nullable=False, index=True) # ACTIVE, INACTIVE, SUSPENDED, TERMINATED
    joined_date = db.Column(db.Date, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)

    # Relationships
    company = db.relationship("Company", back_populates="employees")
    department = db.relationship("Department", back_populates="employees", foreign_keys=[department_id])
    user = db.relationship("User", back_populates="employee", uselist=False)
    devices = db.relationship("Device", back_populates="employee")
    work_sessions = db.relationship("WorkSession", back_populates="employee", cascade="all, delete-orphan")
    attendance_records = db.relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    events = db.relationship("Event", back_populates="employee")
    alerts = db.relationship("Alert", back_populates="employee")

    __table_args__ = (
        db.UniqueConstraint("company_id", "employee_code", name="uq_company_employee_code"),
        db.UniqueConstraint("company_id", "email", name="uq_company_employee_email"),
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        d = super().to_dict()
        d["full_name"] = self.full_name
        d["department_name"] = self.department.name if self.department else None
        return d

    def __repr__(self):
        return f"<Employee {self.employee_code}: {self.full_name}>"
