from datetime import datetime, timezone
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.extensions import db
from app.models.user import User
from app.services.audit_service import AuditService

class AuthService:
    """Service handling credential verification, JWT issuance, and sessions."""

    @staticmethod
    def authenticate(username_or_email: str, password: str):
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email),
            User.is_active == True
        ).first()

        if not user or not user.check_password(password):
            return None, "Invalid username or password"

        if user.status != "ACTIVE":
            return None, "User account is suspended or disabled"

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        # Build claims
        roles = [r.name for r in user.roles if r.is_active]
        permissions = list(user.permissions)
        claims = {
            "company_id": user.company_id,
            "username": user.username,
            "is_superuser": user.is_superuser,
            "roles": roles,
            "permissions": permissions,
            "email": user.email,
            "full_name": user.employee.full_name if user.employee else user.username
        }

        access_token = create_access_token(identity=user.id, additional_claims=claims)
        refresh_token = create_refresh_token(identity=user.id, additional_claims={"company_id": user.company_id})

        AuditService.log_action(
            action="USER_LOGIN_SUCCESS",
            resource_type="user",
            resource_id=user.id,
            company_id=user.company_id
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user.to_dict()
        }, None

    @staticmethod
    def refresh_user_token(refresh_token_str: str):
        try:
            decoded = decode_token(refresh_token_str)
            user_id = decoded["sub"]
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if not user or user.status != "ACTIVE":
                return None, "Invalid or deactivated user"

            roles = [r.name for r in user.roles if r.is_active]
            claims = {
                "company_id": user.company_id,
                "username": user.username,
                "is_superuser": user.is_superuser,
                "roles": roles,
                "permissions": list(user.permissions),
                "email": user.email,
                "full_name": user.employee.full_name if user.employee else user.username
            }
            new_access_token = create_access_token(identity=user.id, additional_claims=claims)
            return {"access_token": new_access_token}, None
        except Exception as e:
            return None, f"Failed to refresh token: {str(e)}"
