from flask import Blueprint, request
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import PERM_DEVICES_VIEW, PERM_DEVICES_MANAGE
from app.middleware.authentication import get_current_user
from app.modules.devices.schemas import DeviceUpdateRequest, DeviceAssignEmployeeRequest
from app.modules.devices.service import DeviceService
from app.utils.pagination import paginate_query
from app.utils.validators import validate_request
from app.utils.response import success_response, error_response

devices_bp = Blueprint("devices", __name__, url_prefix="/api/v1/devices")

@devices_bp.route("", methods=["GET"])
@require_permission(PERM_DEVICES_VIEW)
def list_devices():
    """
    List registered devices combining PostgreSQL persistent state with Redis live status.
    GET /api/v1/devices?page=1&page_size=25&search=PC-001&status=ONLINE
    """
    user = get_current_user()
    status = request.args.get("status")
    search = request.args.get("search")
    unassigned = request.args.get("unassigned") == "true"
    employee_id = request.args.get("employee_id")
    department_id = request.args.get("department_id")
    agent_version = request.args.get("agent_version")

    query = DeviceService.get_devices_query(
        company_id=user.company_id,
        status=status,
        search=search,
        unassigned=unassigned,
        employee_id=employee_id,
        department_id=department_id,
        agent_version=agent_version
    )
    result = paginate_query(query)
    return success_response(data=result)

@devices_bp.route("/<string:device_id>", methods=["GET"])
@require_permission(PERM_DEVICES_VIEW)
def get_device(device_id: str):
    """
    Retrieve full device detail, assigned employee, agent, live presence, and history.
    GET /api/v1/devices/<device_id>
    """
    user = get_current_user()
    detail = DeviceService.get_device_detail(user.company_id, device_id)
    if not detail:
        return error_response(message="Device not found", status_code=404)
    return success_response(data=detail)

@devices_bp.route("/<string:device_id>", methods=["PUT", "PATCH"])
@require_permission(PERM_DEVICES_MANAGE)
@validate_request(DeviceUpdateRequest)
def update_device(device_id: str, validated_data: DeviceUpdateRequest):
    user = get_current_user()
    dev, err = DeviceService.update_device(
        user.company_id,
        device_id,
        validated_data.model_dump(exclude_unset=True)
    )
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=dev.to_dict(), message="Device updated successfully")

@devices_bp.route("/<string:device_id>/assign", methods=["POST"])
@require_permission(PERM_DEVICES_MANAGE)
def assign_employee(device_id: str):
    """
    Assign an employee to a workstation device.
    POST /api/v1/devices/<device_id>/assign
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}
    employee_id = data.get("employee_id")
    
    dev, err = DeviceService.assign_employee(user.company_id, device_id, employee_id)
    if err:
        return error_response(message=err, status_code=400)
    
    action_msg = "Employee assigned to device successfully" if employee_id else "Device unassigned successfully"
    return success_response(data=dev.to_dict(), message=action_msg)

@devices_bp.route("/<string:device_id>/unassign", methods=["POST"])
@require_permission(PERM_DEVICES_MANAGE)
def unassign_employee(device_id: str):
    """
    Unassign any employee from a workstation device.
    POST /api/v1/devices/<device_id>/unassign
    """
    user = get_current_user()
    dev, err = DeviceService.assign_employee(user.company_id, device_id, employee_id=None)
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=dev.to_dict(), message="Device unassigned successfully")

@devices_bp.route("/<string:device_id>/disable", methods=["POST"])
@require_permission(PERM_DEVICES_MANAGE)
def disable_device(device_id: str):
    """
    Administratively disable a workstation device.
    POST /api/v1/devices/<device_id>/disable
    """
    user = get_current_user()
    dev, err = DeviceService.disable_device(user.company_id, device_id)
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=dev.to_dict(), message="Device disabled successfully")

@devices_bp.route("/<string:device_id>/enable", methods=["POST"])
@require_permission(PERM_DEVICES_MANAGE)
def enable_device(device_id: str):
    """
    Re-enable a disabled workstation device.
    POST /api/v1/devices/<device_id>/enable
    """
    user = get_current_user()
    dev, err = DeviceService.enable_device(user.company_id, device_id)
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=dev.to_dict(), message="Device enabled successfully")

@devices_bp.route("/<string:device_id>", methods=["DELETE"])
@require_permission(PERM_DEVICES_MANAGE)
def delete_device(device_id: str):
    user = get_current_user()
    success, err = DeviceService.delete_device(user.company_id, device_id)
    if err:
        return error_response(message=err, status_code=400)
    return success_response(message="Device deleted successfully")
