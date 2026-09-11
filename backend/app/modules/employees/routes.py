from flask import Blueprint, request
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import (
    PERM_EMPLOYEES_VIEW,
    PERM_EMPLOYEES_CREATE,
    PERM_EMPLOYEES_EDIT,
    PERM_EMPLOYEES_DEACTIVATE
)
from app.middleware.authentication import get_current_user
from app.modules.employees.schemas import (
    EmployeeCreateRequest,
    EmployeeUpdateRequest,
    AssignDeviceRequest
)
from app.modules.employees.service import EmployeeService
from app.models.employee import Employee
from app.utils.pagination import paginate_query
from app.utils.validators import validate_request
from app.utils.response import success_response, error_response

employees_bp = Blueprint("employees", __name__, url_prefix="/api/v1/employees")

@employees_bp.route("", methods=["GET"])
@require_permission(PERM_EMPLOYEES_VIEW)
def list_employees():
    user = get_current_user()
    search = request.args.get("search")
    dept_id = request.args.get("department_id")
    status = request.args.get("status")

    query = EmployeeService.get_employees_query(
        company_id=user.company_id,
        search=search,
        department_id=dept_id,
        status=status
    )
    result = paginate_query(query)
    return success_response(data=result)

@employees_bp.route("/<string:employee_id>", methods=["GET"])
@require_permission(PERM_EMPLOYEES_VIEW)
def get_employee(employee_id: str):
    user = get_current_user()
    emp = Employee.query.filter_by(id=employee_id, company_id=user.company_id, is_active=True).first()
    if not emp:
        return error_response(message="Employee not found", status_code=404)
    data = emp.to_dict()
    data["devices"] = [d.to_dict() for d in emp.devices if d.is_active]
    return success_response(data=data)

@employees_bp.route("", methods=["POST"])
@require_permission(PERM_EMPLOYEES_CREATE)
@validate_request(EmployeeCreateRequest)
def create_employee(validated_data: EmployeeCreateRequest):
    user = get_current_user()
    emp, err = EmployeeService.create_employee(
        company_id=user.company_id,
        data=validated_data.model_dump()
    )
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=emp.to_dict(), message="Employee created successfully", status_code=201)

@employees_bp.route("/<string:employee_id>", methods=["PUT", "PATCH"])
@require_permission(PERM_EMPLOYEES_EDIT)
@validate_request(EmployeeUpdateRequest)
def update_employee(employee_id: str, validated_data: EmployeeUpdateRequest):
    user = get_current_user()
    emp, err = EmployeeService.update_employee(
        company_id=user.company_id,
        employee_id=employee_id,
        data=validated_data.model_dump(exclude_unset=True)
    )
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=emp.to_dict(), message="Employee updated successfully")

@employees_bp.route("/<string:employee_id>", methods=["DELETE"])
@require_permission(PERM_EMPLOYEES_DEACTIVATE)
def deactivate_employee(employee_id: str):
    user = get_current_user()
    success, err = EmployeeService.deactivate_employee(
        company_id=user.company_id,
        employee_id=employee_id
    )
    if err:
        return error_response(message=err, status_code=400)
    return success_response(message="Employee deactivated successfully")

@employees_bp.route("/<string:employee_id>/assign-device", methods=["POST"])
@require_permission(PERM_EMPLOYEES_EDIT)
@validate_request(AssignDeviceRequest)
def assign_device(employee_id: str, validated_data: AssignDeviceRequest):
    user = get_current_user()
    emp, err = EmployeeService.assign_device(
        company_id=user.company_id,
        employee_id=employee_id,
        device_id=validated_data.device_id
    )
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=emp.to_dict(), message="Device assigned successfully")
