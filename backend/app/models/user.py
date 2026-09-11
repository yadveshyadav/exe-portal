import bcrypt
from app.extensions import db
from app.models.base import BaseModel
from app.models.role import user_roles

class User(BaseModel):
    """Admin portal user account."""
    __tablename__ = "users"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, unique=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(30), default="ACTIVE", nullable=False) # ACTIVE, DISABLED, LOCKED
    last_login = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    company = db.relationship("Company", back_populates="users")
    employee = db.relationship("Employee", back_populates="user", foreign_keys=[employee_id])
    roles = db.relationship("Role", secondary=user_roles, back_populates="users")
    audit_logs = db.relationship("AuditLog", back_populates="user")

    __table_args__ = (
        db.UniqueConstraint("company_id", "username", name="uq_company_username"),
        db.UniqueConstraint("company_id", "email", name="uq_company_user_email"),
    )

    def set_password(self, raw_password: str):
        """Hash raw password with bcrypt salt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(raw_password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """Verify candidate raw password against bcrypt hash."""
        if not self.password_hash:
            return False
        return bcrypt.checkpw(raw_password.encode("utf-8"), self.password_hash.encode("utf-8"))

    @property
    def permissions(self) -> set:
        """Resolve all distinct permission codes assigned to this user through roles."""
        if self.is_superuser:
            # Superuser has implicit wildcard access
            return {"*"}
        perms = set()
        for role in self.roles:
            if role.is_active:
                for perm in role.permissions:
                    if perm.is_active:
                        perms.add(perm.code)
        return perms

    def has_permission(self, permission_code: str) -> bool:
        """Check if user has a specific permission or wildcard superuser privilege."""
        if self.is_superuser:
            return True
        user_perms = self.permissions
        if "*" in user_perms:
            return True
        return permission_code in user_perms

    def to_dict(self, include_roles=True):
        data = super().to_dict()
        data.pop("password_hash", None)
        if include_roles:
            data["roles"] = [r.name for r in self.roles if r.is_active]
            data["permissions"] = list(self.permissions)
        data["full_name"] = self.employee.full_name if self.employee else self.username
        return data

    def __repr__(self):
        return f"<User {self.username}>"
