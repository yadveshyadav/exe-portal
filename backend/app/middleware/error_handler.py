import traceback
from flask import jsonify
from werkzeug.exceptions import HTTPException
from app.utils.response import error_response
from app.extensions import jwt

def register_error_handlers(app):
    """Register custom JSON error handlers for standard HTTP errors and exceptions."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return error_response(
            message=e.description,
            errors=[e.name],
            status_code=e.code
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(e):
        app.logger.error(f"Unhandled Exception: {str(e)}\n{traceback.format_exc()}")
        if app.config.get("DEBUG"):
            return error_response(
                message=str(e),
                errors=[traceback.format_exc()],
                status_code=500
            )
        return error_response(
            message="An unexpected server error occurred. Please contact system administrator.",
            status_code=500
        )

    # JWT Error handlers
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return error_response(
            message="Missing or invalid authentication token",
            status_code=401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return error_response(
            message="Invalid authentication token signature or structure",
            status_code=401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response(
            message="Authentication token has expired. Please refresh your session.",
            status_code=401
        )

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return error_response(
            message="Authentication token has been revoked",
            status_code=401
        )
