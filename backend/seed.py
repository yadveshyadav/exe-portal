import os
from app import create_app
from app.extensions import db
from app.models.company import Company
from app.models.department import Department
from app.models.employee import Employee
from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.device import Device
from app.models.agent import Agent
from app.models.policy import Policy, PolicyRule
from app.models.event import Event
from app.models.work_session import WorkSession
from app.models.attendance import Attendance
from app.models.alert import Alert
from app.models.command import Command, CommandResult
from app.models.audit_log import AuditLog
from app.modules.auth.permissions import DEFAULT_PERMISSIONS

def seed_essential_only():
    """Seeds only the essential infrastructure: Permissions, Roles, Company, and Admin account. No dummy employees, devices, or events."""
    app = create_app(os.getenv("FLASK_ENV", "development"))
    with app.app_context():
        print("[*] Clearing all dummy data from tables...")
        # Clear operational tables
        CommandResult.query.delete()
        Command.query.delete()
        Alert.query.delete()
        Event.query.delete()
        WorkSession.query.delete()
        Attendance.query.delete()
        Agent.query.delete()
        Device.query.delete()
        Employee.query.delete()
        Department.query.delete()
        PolicyRule.query.delete()
        Policy.query.delete()
        AuditLog.query.delete()
        db.session.commit()

        print("[*] Ensuring system permissions exist...")
        perm_map = {}
        for code, name, module in DEFAULT_PERMISSIONS:
            perm = Permission.query.filter_by(code=code).first()
            if not perm:
                perm = Permission(code=code, name=name, module=module)
                db.session.add(perm)
            perm_map[code] = perm
        db.session.commit()

        print("[*] Ensuring default company exists...")
        company = Company.query.filter_by(code="ACME").first()
        if not company:
            company = Company(
                code="ACME",
                name="Acme Corporation",
                domain="acme.corp",
                settings={
                    "agent_config": {
                        "heartbeat_interval_seconds": 30,
                        "idle_threshold_seconds": 300,
                        "reconnect_interval_seconds": 15,
                        "event_batch_size": 20,
                        "log_retention_days": 90
                    }
                }
            )
            db.session.add(company)
            db.session.flush()

        print("[*] Ensuring system roles exist...")
        # Super Admin
        super_admin_role = Role.query.filter_by(company_id=company.id, code="SUPER_ADMIN").first()
        if not super_admin_role:
            super_admin_role = Role(
                company_id=company.id,
                name="Super Administrator",
                code="SUPER_ADMIN",
                description="Unrestricted full system administrative access",
                is_system=True
            )
            db.session.add(super_admin_role)
        super_admin_role.permissions = list(perm_map.values())

        # Admin
        admin_role = Role.query.filter_by(company_id=company.id, code="ADMIN").first()
        if not admin_role:
            admin_role = Role(
                company_id=company.id,
                name="Portal Administrator",
                code="ADMIN",
                description="Manage workforce, devices, monitoring, and policies",
                is_system=True
            )
            db.session.add(admin_role)
        admin_role.permissions = [
            p for code, p in perm_map.items() 
            if not code.startswith("users.") and not code.startswith("roles.")
        ]

        # Auditor
        auditor_role = Role.query.filter_by(company_id=company.id, code="AUDITOR").first()
        if not auditor_role:
            auditor_role = Role(
                company_id=company.id,
                name="Security Auditor",
                code="AUDITOR",
                description="Read-only access to monitoring, events, and audit logs",
                is_system=True
            )
            db.session.add(auditor_role)
        auditor_role.permissions = [p for code, p in perm_map.items() if ".view" in code]

        # Viewer
        viewer_role = Role.query.filter_by(company_id=company.id, code="VIEWER").first()
        if not viewer_role:
            viewer_role = Role(
                company_id=company.id,
                name="Workforce Viewer",
                code="VIEWER",
                description="Read-only view for workforce dashboards",
                is_system=True
            )
            db.session.add(viewer_role)
        viewer_role.permissions = [
            perm_map.get("dashboard.view"),
            perm_map.get("monitoring.view"),
            perm_map.get("attendance.view")
        ]

        db.session.commit()

        print("[*] Ensuring SuperAdmin account exists...")
        admin_user = User.query.filter_by(company_id=company.id, username="admin").first()
        if not admin_user:
            admin_user = User(
                company_id=company.id,
                username="admin",
                email="admin@acme.corp",
                is_superuser=True,
                status="ACTIVE"
            )
            admin_user.set_password("Admin@123456")
            admin_user.roles = [super_admin_role]
            db.session.add(admin_user)
        else:
            admin_user.roles = [super_admin_role]

        db.session.commit()
        print("[+] Clean database initialized! All dummy data removed.")

if __name__ == "__main__":
    seed_essential_only()
