from datetime import datetime
from flask import Blueprint, request
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import PERM_ATTENDANCE_VIEW
from app.middleware.authentication import get_current_user
from app.models.attendance import Attendance
from app.utils.pagination import paginate_query
from app.utils.response import success_response

attendance_bp = Blueprint("attendance", __name__, url_prefix="/api/v1/attendance")

@attendance_bp.route("", methods=["GET"])
@require_permission(PERM_ATTENDANCE_VIEW)
def list_attendance():
    user = get_current_user()
    emp_id = request.args.get("employee_id")
    date_str = request.args.get("date")

    query = Attendance.query.filter_by(company_id=user.company_id)
    if emp_id:
        query = query.filter_by(employee_id=emp_id)
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter_by(attendance_date=target_date)
        except ValueError:
            pass

    query = query.order_by(Attendance.attendance_date.desc())
    result = paginate_query(query)
    return success_response(data=result)
