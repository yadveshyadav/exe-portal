from app.extensions import db
from app.models.base import BaseModel
from app.models.permission import role_permissions

# Association table between users and roles
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.String(36), db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("assigned_at", db.DateTime(timezone=True), default=db.func.now()),
    db.Column("assigned_by", db.String(36), nullable=True)
)

class Role(BaseModel):
    """System and custom security roles."""
    __tablename__ = "roles"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, index=True) # e.g. 'SUPER_ADMIN', 'ADMIN', 'AUDITOR', 'VIEWER'
    description = db.Column(db.String(255), nullable=True)
    is_system = db.Column(db.Boolean, default=False, nullable=False) # Protected system roles

    # Relationships
    company = db.relationship("Company", back_populates="roles")
    users = db.relationship("User", secondary=user_roles, back_populates="roles")
    permissions = db.relationship("Permission", secondary=role_permissions, back_populates="roles")

    __table_args__ = (
        db.UniqueConstraint("company_id", "code", name="uq_company_role_code"),
    )

    def __repr__(self):
        return f"<Role {self.code}>"
