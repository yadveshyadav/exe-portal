import uuid
from datetime import datetime, timezone
from app.extensions import db

def get_utc_now():
    return datetime.now(timezone.utc)

class BaseModel(db.Model):
    """Abstract base model with UUID primary keys and standard audit timestamps."""
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, nullable=False, index=True)
    updated_at = db.Column(db.DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Convert model instance into dictionary."""
        result = {}
        for col in self.__table__.columns:
            val = getattr(self, col.name)
            if isinstance(val, datetime):
                result[col.name] = val.isoformat()
            else:
                result[col.name] = val
        return result
