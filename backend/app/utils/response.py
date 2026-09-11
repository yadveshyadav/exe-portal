from flask import jsonify

def api_response(success=True, data=None, message=None, errors=None, status_code=200):
    """Standardized API JSON response structure."""
    payload = {
        "success": success,
        "data": data if data is not None else {},
        "message": message,
        "errors": errors or []
    }
    return jsonify(payload), status_code

def success_response(data=None, message=None, status_code=200):
    return api_response(success=True, data=data, message=message, status_code=status_code)

def error_response(message="An error occurred", errors=None, status_code=400):
    if errors is None:
        errors = [message] if message else []
    return api_response(success=False, data={}, message=message, errors=errors, status_code=status_code)
