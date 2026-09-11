from app.extensions import db
from app.models.base import BaseModel

# Association table between roles and permissions
role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.String(36), db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("permission_id", db.String(36), db.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    db.Column("assigned_at", db.DateTime(timezone=True), default=db.func.now())
)

class Permission(BaseModel):
    """Granular system permission."""
    __tablename__ = "permissions"

    code = db.Column(db.String(100), unique=True, nullable=False, index=True) # e.g. 'employees.view', 'devices.manage'
    name = db.Column(db.String(150), nullable=False)
    module = db.Column(db.String(50), nullable=False, index=True) # e.g. 'workforce', 'devices', 'monitoring'
    description = db.Column(db.String(255), nullable=True)

    roles = db.relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission {self.code}>"
