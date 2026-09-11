from flask import Blueprint
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import PERM_DASHBOARD_VIEW
from app.middleware.authentication import get_current_user
from app.modules.dashboard.service import DashboardService
from app.utils.response import success_response

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/v1/dashboard")

@dashboard_bp.route("/summary", methods=["GET"])
@require_permission(PERM_DASHBOARD_VIEW)
def summary():
    user = get_current_user()
    data = DashboardService.get_summary(user.company_id)
    return success_response(data=data)

@dashboard_bp.route("/recent-events", methods=["GET"])
@require_permission(PERM_DASHBOARD_VIEW)
def recent_events():
    user = get_current_user()
    events = DashboardService.get_recent_events(user.company_id, limit=15)
    return success_response(data={"events": events})
