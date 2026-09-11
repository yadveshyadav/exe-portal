from app.extensions import db
from app.models.base import BaseModel

class Policy(BaseModel):
    """Central agent configuration policy."""
    __tablename__ = "policies"

    company_id = db.Column(db.String(36), db.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    version = db.Column(db.String(20), default="1.0", nullable=False)
    priority = db.Column(db.Integer, default=100, nullable=False)

    # Relationships
    company = db.relationship("Company", back_populates="policies")
    rules = db.relationship("PolicyRule", back_populates="policy", cascade="all, delete-orphan")

    __table_args__ = (
        db.UniqueConstraint("company_id", "code", name="uq_company_policy_code"),
    )

    def to_dict(self):
        d = super().to_dict()
        d["rules"] = [r.to_dict() for r in self.rules]
        return d

    def __repr__(self):
        return f"<Policy {self.code}: {self.name}>"


class PolicyRule(BaseModel):
    """Individual rule configuration parameter within a policy."""
    __tablename__ = "policy_rules"

    policy_id = db.Column(db.String(36), db.ForeignKey("policies.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_type = db.Column(db.String(50), nullable=False, index=True) 
    # e.g., 'HEARTBEAT_INTERVAL', 'IDLE_THRESHOLD', 'RECONNECT_INTERVAL', 'BATCH_SIZE', 'AGENT_VERSION_POLICY'
    rule_value = db.Column(db.JSON, nullable=False)

    # Relationships
    policy = db.relationship("Policy", back_populates="rules")

    def __repr__(self):
        return f"<PolicyRule {self.rule_type}>"
