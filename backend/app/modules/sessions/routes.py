from flask import Blueprint, request
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import PERM_ATTENDANCE_VIEW
from app.middleware.authentication import get_current_user
from app.models.work_session import WorkSession
from app.utils.pagination import paginate_query
from app.utils.response import success_response

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/v1/sessions")

@sessions_bp.route("", methods=["GET"])
@require_permission(PERM_ATTENDANCE_VIEW)
def list_sessions():
    user = get_current_user()
    emp_id = request.args.get("employee_id")
    device_id = request.args.get("device_id")

    query = WorkSession.query.filter_by(company_id=user.company_id)
    if emp_id:
        query = query.filter_by(employee_id=emp_id)
    if device_id:
        query = query.filter_by(device_id=device_id)

    query = query.order_by(WorkSession.start_time.desc())
    result = paginate_query(query)
    return success_response(data=result)
