from functools import wraps
from flask_jwt_extended import verify_jwt_in_request
from app.middleware.authentication import get_current_user
from app.utils.response import error_response

def require_permission(permission_code: str):
    """Enforce granular role-based access control permission on an API endpoint."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Verify JWT header first
            try:
                verify_jwt_in_request()
            except Exception as e:
                return error_response(
                    message="Authentication required",
                    errors=[str(e)],
                    status_code=401
                )

            user = get_current_user()
            if not user:
                return error_response(
                    message="Authenticated user account not found or deactivated",
                    status_code=401
                )

            if user.status != "ACTIVE":
                return error_response(
                    message="User account is locked or disabled",
                    status_code=403
                )

            # Check permission or superuser override
            if not user.has_permission(permission_code):
                return error_response(
                    message=f"Access denied: Missing required permission '{permission_code}'",
                    errors=[f"Permission required: {permission_code}"],
                    status_code=403
                )

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_superuser():
    """Enforce superuser privileges on an API endpoint."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = get_current_user()
            if not user or not user.is_superuser:
                return error_response(
                    message="Access denied: Superuser privilege required",
                    status_code=403
                )
            return fn(*args, **kwargs)
        return wrapper
    return decorator
