from app.extensions import db
from app.models.base import BaseModel

class Department(BaseModel):
    """Department hierarchical entity."""
    __tablename__ = "departments"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.String(36), db.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    manager_id = db.Column(db.String(36), db.ForeignKey("employees.id", ondelete="SET NULL", use_alter=True), nullable=True)

    # Relationships
    company = db.relationship("Company", back_populates="departments")
    parent = db.relationship("Department", remote_side="Department.id", backref="sub_departments")
    employees = db.relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")

    __table_args__ = (
        db.UniqueConstraint("company_id", "code", name="uq_company_department_code"),
    )

    def __repr__(self):
        return f"<Department {self.code}: {self.name}>"
