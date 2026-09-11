from app.extensions import db
from app.models.department import Department
from app.services.audit_service import AuditService

class DepartmentService:
    @staticmethod
    def get_departments(company_id: str):
        return Department.query.filter_by(company_id=company_id, is_active=True).order_by(Department.name.asc()).all()

    @staticmethod
    def create_department(company_id: str, data: dict):
        if Department.query.filter_by(company_id=company_id, code=data["code"]).first():
            return None, "Department code already exists"

        dept = Department(
            company_id=company_id,
            name=data["name"],
            code=data["code"],
            description=data.get("description"),
            parent_id=data.get("parent_id"),
            manager_id=data.get("manager_id")
        )
        db.session.add(dept)
        db.session.commit()

        AuditService.log_action(
            action="DEPARTMENT_CREATED",
            resource_type="department",
            resource_id=dept.id,
            after_value=dept.to_dict(),
            company_id=company_id
        )
        return dept, None

    @staticmethod
    def update_department(company_id: str, dept_id: str, data: dict):
        dept = Department.query.filter_by(id=dept_id, company_id=company_id, is_active=True).first()
        if not dept:
            return None, "Department not found"

        before = dept.to_dict()
        for k, v in data.items():
            if v is not None and hasattr(dept, k):
                setattr(dept, k, v)

        db.session.commit()
        AuditService.log_action(
            action="DEPARTMENT_UPDATED",
            resource_type="department",
            resource_id=dept.id,
            before_value=before,
            after_value=dept.to_dict(),
            company_id=company_id
        )
        return dept, None

    @staticmethod
    def delete_department(company_id: str, dept_id: str):
        dept = Department.query.filter_by(id=dept_id, company_id=company_id, is_active=True).first()
        if not dept:
            return False, "Department not found"

        dept.is_active = False
        db.session.commit()
        AuditService.log_action(
            action="DEPARTMENT_DELETED",
            resource_type="department",
            resource_id=dept.id,
            company_id=company_id
        )
        return True, None
