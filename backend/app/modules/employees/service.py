from app.extensions import db
from app.models.employee import Employee
from app.models.device import Device
from app.services.audit_service import AuditService

class EmployeeService:
    @staticmethod
    def get_employees_query(company_id: str, search: str = None, department_id: str = None, status: str = None):
        query = Employee.query.filter_by(company_id=company_id, is_active=True)
        if search:
            search_fmt = f"%{search}%"
            query = query.filter(
                (Employee.first_name.ilike(search_fmt)) |
                (Employee.last_name.ilike(search_fmt)) |
                (Employee.email.ilike(search_fmt)) |
                (Employee.employee_code.ilike(search_fmt))
            )
        if department_id:
            query = query.filter_by(department_id=department_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Employee.created_at.desc())

    @staticmethod
    def create_employee(company_id: str, data: dict):
        # Check uniqueness
        if Employee.query.filter_by(company_id=company_id, employee_code=data["employee_code"]).first():
            return None, "Employee code already exists"
        if Employee.query.filter_by(company_id=company_id, email=data["email"]).first():
            return None, "Email address already registered"

        employee = Employee(
            company_id=company_id,
            employee_code=data["employee_code"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data.get("phone"),
            designation=data.get("designation"),
            department_id=data.get("department_id"),
            status=data.get("status", "ACTIVE")
        )
        db.session.add(employee)
        db.session.commit()

        AuditService.log_action(
            action="EMPLOYEE_CREATED",
            resource_type="employee",
            resource_id=employee.id,
            after_value=employee.to_dict(),
            company_id=company_id
        )
        return employee, None

    @staticmethod
    def update_employee(company_id: str, employee_id: str, data: dict):
        employee = Employee.query.filter_by(id=employee_id, company_id=company_id, is_active=True).first()
        if not employee:
            return None, "Employee not found"

        before = employee.to_dict()
        for k, v in data.items():
            if v is not None and hasattr(employee, k):
                setattr(employee, k, v)

        db.session.commit()
        AuditService.log_action(
            action="EMPLOYEE_UPDATED",
            resource_type="employee",
            resource_id=employee.id,
            before_value=before,
            after_value=employee.to_dict(),
            company_id=company_id
        )
        return employee, None

    @staticmethod
    def deactivate_employee(company_id: str, employee_id: str):
        employee = Employee.query.filter_by(id=employee_id, company_id=company_id, is_active=True).first()
        if not employee:
            return False, "Employee not found"

        employee.status = "INACTIVE"
        # Soft delete flag
        employee.is_active = False
        
        # Unassign associated devices
        for dev in employee.devices:
            dev.employee_id = None

        db.session.commit()
        AuditService.log_action(
            action="EMPLOYEE_DEACTIVATED",
            resource_type="employee",
            resource_id=employee.id,
            company_id=company_id
        )
        return True, None

    @staticmethod
    def assign_device(company_id: str, employee_id: str, device_id: str):
        employee = Employee.query.filter_by(id=employee_id, company_id=company_id, is_active=True).first()
        if not employee:
            return None, "Employee not found"
        device = Device.query.filter_by(id=device_id, company_id=company_id, is_active=True).first()
        if not device:
            return None, "Device not found"

        old_emp_id = device.employee_id
        device.employee_id = employee.id
        db.session.commit()

        AuditService.log_action(
            action="DEVICE_ASSIGNED",
            resource_type="device",
            resource_id=device.id,
            before_value={"employee_id": old_emp_id},
            after_value={"employee_id": employee.id},
            company_id=company_id
        )
        return employee, None
