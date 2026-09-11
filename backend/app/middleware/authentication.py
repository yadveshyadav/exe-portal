from flask import g
from flask_jwt_extended import get_jwt_identity
from app.models.user import User

def get_current_user():
    """Retrieve the currently authenticated User model instance based on JWT identity."""
    if hasattr(g, "current_user") and g.current_user is not None:
        return g.current_user

    try:
        identity = get_jwt_identity()
    except Exception:
        identity = None

    if not identity:
        return None

    user = User.query.filter_by(id=identity, is_active=True).first()
    g.current_user = user
    return user
