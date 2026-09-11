import logging
from flask import request
from app.extensions import db
from app.models.audit_log import AuditLog
from app.middleware.authentication import get_current_user

logger = logging.getLogger(__name__)

class AuditService:
    """Service to record administrative operations and agent events in the audit trail."""

    @staticmethod
    def log_action(
        action: str,
        resource_type: str,
        resource_id: str = None,
        before_value: dict = None,
        after_value: dict = None,
        company_id: str = None,
        result: str = "SUCCESS",
        failure_reason: str = None
    ):
        try:
            current_user = get_current_user()
            user_id = current_user.id if current_user else None
            
            if not company_id and current_user:
                company_id = current_user.company_id

            ip_address = "127.0.0.1"
            user_agent = "System"
            try:
                if request:
                    ip_address = request.remote_addr or "127.0.0.1"
                    user_agent = request.headers.get("User-Agent", "System")
            except Exception:
                pass

            log_entry = AuditLog(
                company_id=company_id,
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                before_value=before_value,
                after_value=after_value,
                ip_address=ip_address,
                user_agent=user_agent[:255] if user_agent else None,
                result=result,
                failure_reason=failure_reason
            )
            db.session.add(log_entry)
            db.session.flush()
            return log_entry
        except Exception as e:
            logger.debug(f"Audit log insertion notice: {e}")
            return None
