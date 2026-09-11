from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.modules.auth.schemas import LoginRequest, RefreshTokenRequest
from app.modules.auth.service import AuthService
from app.middleware.authentication import get_current_user
from app.utils.validators import validate_request
from app.utils.response import success_response, error_response

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

@auth_bp.route("/login", methods=["POST"])
@validate_request(LoginRequest)
def login(validated_data: LoginRequest):
    result, err = AuthService.authenticate(
        username_or_email=validated_data.username_or_email,
        password=validated_data.password
    )
    if err:
        return error_response(message=err, status_code=401)
    return success_response(data=result, message="Login successful")

@auth_bp.route("/refresh", methods=["POST"])
@validate_request(RefreshTokenRequest)
def refresh(validated_data: RefreshTokenRequest):
    result, err = AuthService.refresh_user_token(validated_data.refresh_token)
    if err:
        return error_response(message=err, status_code=401)
    return success_response(data=result, message="Token refreshed")

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = get_current_user()
    if not user:
        return error_response(message="User not found", status_code=404)
    return success_response(data=user.to_dict(), message="User profile retrieved")

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return success_response(message="Logout successful")
