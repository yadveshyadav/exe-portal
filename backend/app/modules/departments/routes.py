from flask import Blueprint
from app.middleware.authorization import require_permission
from app.modules.auth.permissions import PERM_DEPARTMENTS_VIEW, PERM_DEPARTMENTS_MANAGE
from app.middleware.authentication import get_current_user
from app.modules.departments.schemas import DepartmentCreateRequest, DepartmentUpdateRequest
from app.modules.departments.service import DepartmentService
from app.utils.validators import validate_request
from app.utils.response import success_response, error_response

departments_bp = Blueprint("departments", __name__, url_prefix="/api/v1/departments")

@departments_bp.route("", methods=["GET"])
@require_permission(PERM_DEPARTMENTS_VIEW)
def list_departments():
    user = get_current_user()
    departments = DepartmentService.get_departments(user.company_id)
    return success_response(data={"items": [d.to_dict() for d in departments]})

@departments_bp.route("", methods=["POST"])
@require_permission(PERM_DEPARTMENTS_MANAGE)
@validate_request(DepartmentCreateRequest)
def create_department(validated_data: DepartmentCreateRequest):
    user = get_current_user()
    dept, err = DepartmentService.create_department(user.company_id, validated_data.model_dump())
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=dept.to_dict(), message="Department created successfully", status_code=201)

@departments_bp.route("/<string:dept_id>", methods=["PUT", "PATCH"])
@require_permission(PERM_DEPARTMENTS_MANAGE)
@validate_request(DepartmentUpdateRequest)
def update_department(dept_id: str, validated_data: DepartmentUpdateRequest):
    user = get_current_user()
    dept, err = DepartmentService.update_department(user.company_id, dept_id, validated_data.model_dump(exclude_unset=True))
    if err:
        return error_response(message=err, status_code=400)
    return success_response(data=dept.to_dict(), message="Department updated successfully")

@departments_bp.route("/<string:dept_id>", methods=["DELETE"])
@require_permission(PERM_DEPARTMENTS_MANAGE)
def delete_department(dept_id: str):
    user = get_current_user()
    success, err = DepartmentService.delete_department(user.company_id, dept_id)
    if err:
        return error_response(message=err, status_code=400)
    return success_response(message="Department deleted successfully")
