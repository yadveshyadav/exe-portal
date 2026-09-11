from flask import Blueprint, request
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import PERM_MONITORING_HISTORY
from app.middleware.authentication import get_current_user
from app.models.event import Event
from app.utils.pagination import paginate_query
from app.utils.response import success_response

events_bp = Blueprint("events", __name__, url_prefix="/api/v1/events")

@events_bp.route("", methods=["GET"])
@require_permission(PERM_MONITORING_HISTORY)
def list_events():
    user = get_current_user()
    device_id = request.args.get("device_id")
    employee_id = request.args.get("employee_id")
    event_type = request.args.get("event_type")
    severity = request.args.get("severity")

    query = Event.query.filter_by(company_id=user.company_id)
    if device_id:
        query = query.filter_by(device_id=device_id)
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    if event_type:
        query = query.filter_by(event_type=event_type)
    if severity:
        query = query.filter_by(severity=severity)

    query = query.order_by(Event.received_at.desc())
    result = paginate_query(query)
    return success_response(data=result)
