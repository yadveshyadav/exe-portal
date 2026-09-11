from functools import wraps
from flask import request
from pydantic import ValidationError
from app.utils.response import error_response

def validate_request(schema_class):
    """Decorator to validate incoming JSON payload against a Pydantic model."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return error_response(
                    message="Content-Type must be application/json", 
                    status_code=415
                )
            
            payload = request.get_json(silent=True)
            if payload is None:
                payload = {}
                
            try:
                validated_data = schema_class(**payload)
                # Pass validated instance as keyword argument 'payload'
                return fn(*args, validated_data=validated_data, **kwargs)
            except ValidationError as err:
                error_list = []
                for error in err.errors():
                    field = " -> ".join(str(loc) for loc in error.get("loc", []))
                    msg = error.get("msg", "Invalid value")
                    error_list.append(f"{field}: {msg}" if field else msg)
                return error_response(
                    message="Validation failed", 
                    errors=error_list, 
                    status_code=422
                )
        return wrapper
    return decorator
