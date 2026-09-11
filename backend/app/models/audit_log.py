from app.extensions import db
from app.models.base import BaseModel

class AuditLog(BaseModel):
    """Immutable audit trail for administrative operations."""
    __tablename__ = "audit_logs"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action = db.Column(db.String(100), nullable=False, index=True) 
    # e.g., EMPLOYEE_CREATED, DEVICE_ASSIGNED, POLICY_UPDATED, ROLE_CHANGED, etc.
    
    resource_type = db.Column(db.String(50), nullable=False, index=True) # employee, device, policy, user, role
    resource_id = db.Column(db.String(36), nullable=True, index=True)
    
    before_value = db.Column(db.JSON, nullable=True)
    after_value = db.Column(db.JSON, nullable=True)
    
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    result = db.Column(db.String(20), default="SUCCESS", nullable=False) # SUCCESS, FAILURE
    failure_reason = db.Column(db.Text, nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="audit_logs")

    def to_dict(self):
        d = super().to_dict()
        d["username"] = self.user.username if self.user else "System / Agent"
        return d

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.resource_type}:{self.resource_id} by {self.user_id}>"
