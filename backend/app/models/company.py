from app.extensions import db
from app.models.base import BaseModel

class Company(BaseModel):
    """Company / Organization multi-tenant root entity."""
    __tablename__ = "companies"

    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    domain = db.Column(db.String(255), nullable=True)
    settings = db.Column(db.JSON, default=dict, nullable=False)

    # Relationships
    departments = db.relationship("Department", back_populates="company", cascade="all, delete-orphan")
    employees = db.relationship("Employee", back_populates="company", cascade="all, delete-orphan")
    users = db.relationship("User", back_populates="company", cascade="all, delete-orphan")
    devices = db.relationship("Device", back_populates="company", cascade="all, delete-orphan")
    roles = db.relationship("Role", back_populates="company", cascade="all, delete-orphan")
    policies = db.relationship("Policy", back_populates="company", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Company {self.code}: {self.name}>"
