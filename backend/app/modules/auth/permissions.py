# Core System Permission Constants

PERM_DASHBOARD_VIEW = "dashboard.view"

PERM_EMPLOYEES_VIEW = "employees.view"
PERM_EMPLOYEES_CREATE = "employees.create"
PERM_EMPLOYEES_EDIT = "employees.edit"
PERM_EMPLOYEES_DEACTIVATE = "employees.deactivate"

PERM_DEPARTMENTS_VIEW = "departments.view"
PERM_DEPARTMENTS_MANAGE = "departments.manage"

PERM_DEVICES_VIEW = "devices.view"
PERM_DEVICES_MANAGE = "devices.manage"

PERM_AGENTS_VIEW = "agents.view"
PERM_AGENTS_MANAGE = "agents.manage"

PERM_MONITORING_VIEW = "monitoring.view"
PERM_MONITORING_HISTORY = "monitoring.history"

PERM_ATTENDANCE_VIEW = "attendance.view"
PERM_REPORTS_VIEW = "reports.view"

PERM_POLICIES_VIEW = "policies.view"
PERM_POLICIES_MANAGE = "policies.manage"

PERM_ALERTS_VIEW = "alerts.view"
PERM_ALERTS_MANAGE = "alerts.manage"

PERM_COMMANDS_VIEW = "commands.view"
PERM_COMMANDS_DISPATCH = "commands.dispatch"

PERM_USERS_VIEW = "users.view"
PERM_USERS_MANAGE = "users.manage"

PERM_ROLES_VIEW = "roles.view"
PERM_ROLES_MANAGE = "roles.manage"

PERM_PERMISSIONS_VIEW = "permissions.view"

PERM_AUDIT_VIEW = "audit.view"

PERM_SETTINGS_VIEW = "settings.view"
PERM_SETTINGS_MANAGE = "settings.manage"

DEFAULT_PERMISSIONS = [
    # Dashboard
    (PERM_DASHBOARD_VIEW, "View Dashboard Metrics", "dashboard"),
    
    # Workforce
    (PERM_EMPLOYEES_VIEW, "View Employees List & Profiles", "workforce"),
    (PERM_EMPLOYEES_CREATE, "Create New Employee Profile", "workforce"),
    (PERM_EMPLOYEES_EDIT, "Edit Employee Details & Assignment", "workforce"),
    (PERM_EMPLOYEES_DEACTIVATE, "Deactivate Employee", "workforce"),
    (PERM_DEPARTMENTS_VIEW, "View Departments", "workforce"),
    (PERM_DEPARTMENTS_MANAGE, "Manage Departments", "workforce"),
    (PERM_ATTENDANCE_VIEW, "View Attendance & Work Sessions", "workforce"),
    
    # Devices & Agents
    (PERM_DEVICES_VIEW, "View Enrolled Devices", "devices"),
    (PERM_DEVICES_MANAGE, "Manage Devices & Assignments", "devices"),
    (PERM_AGENTS_VIEW, "View Agents & Versions", "devices"),
    (PERM_AGENTS_MANAGE, "Manage Agent Configuration", "devices"),
    
    # Monitoring
    (PERM_MONITORING_VIEW, "View Live Workforce Monitoring", "monitoring"),
    (PERM_MONITORING_HISTORY, "View Historical Event Logs", "monitoring"),
    
    # Control & Policies
    (PERM_POLICIES_VIEW, "View Policies", "control"),
    (PERM_POLICIES_MANAGE, "Create & Edit Agent Policies", "control"),
    (PERM_ALERTS_VIEW, "View System Alerts", "control"),
    (PERM_ALERTS_MANAGE, "Manage & Resolve Alerts", "control"),
    (PERM_COMMANDS_VIEW, "View Dispatched Commands", "control"),
    (PERM_COMMANDS_DISPATCH, "Dispatch Safe Commands to Agents", "control"),
    
    # Reports
    (PERM_REPORTS_VIEW, "Generate & Export Reports", "reports"),
    
    # Administration
    (PERM_USERS_VIEW, "View Portal Users", "administration"),
    (PERM_USERS_MANAGE, "Create & Manage Users", "administration"),
    (PERM_ROLES_VIEW, "View Roles", "administration"),
    (PERM_ROLES_MANAGE, "Create & Modify Roles", "administration"),
    (PERM_PERMISSIONS_VIEW, "View Permissions Catalog", "administration"),
    (PERM_AUDIT_VIEW, "View Immutable Audit Logs", "administration"),
    
    # Settings
    (PERM_SETTINGS_VIEW, "View Portal Settings", "settings"),
    (PERM_SETTINGS_MANAGE, "Modify System & Company Settings", "settings"),
]
