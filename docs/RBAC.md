# Role-Based Access Control (RBAC) Specification

## 1. System Roles Matrix

| Permission Code | Description | SuperAdmin | Admin | Auditor | Viewer |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `dashboard.view` | View Dashboard Overview | ✓ | ✓ | ✓ | ✓ |
| `employees.view` | View Workforce Directory | ✓ | ✓ | ✓ |  |
| `employees.create` | Add New Employee Profile | ✓ | ✓ |  |  |
| `employees.edit` | Update Employee Profile & Devices | ✓ | ✓ |  |  |
| `employees.deactivate` | Deactivate Employee Record | ✓ | ✓ |  |  |
| `departments.view` | View Departments | ✓ | ✓ | ✓ |  |
| `departments.manage` | Create/Edit Departments | ✓ | ✓ |  |  |
| `devices.view` | View Enrolled Devices | ✓ | ✓ | ✓ |  |
| `devices.manage` | Manage Device Assignments | ✓ | ✓ |  |  |
| `agents.view` | View Agent Versions | ✓ | ✓ | ✓ |  |
| `agents.manage` | Push Agent Configuration | ✓ | ✓ |  |  |
| `monitoring.view` | Live Workforce Stream | ✓ | ✓ | ✓ | ✓ |
| `monitoring.history` | Event Stream Logs | ✓ | ✓ | ✓ |  |
| `attendance.view` | View Attendance & Sessions | ✓ | ✓ | ✓ | ✓ |
| `policies.view` | View Policies | ✓ | ✓ | ✓ |  |
| `policies.manage` | Modify Telemetry Policies | ✓ | ✓ |  |  |
| `alerts.view` | View Active Alerts | ✓ | ✓ | ✓ |  |
| `alerts.manage` | Acknowledge & Resolve Alerts | ✓ | ✓ |  |  |
| `commands.view` | View Dispatched Commands | ✓ | ✓ | ✓ |  |
| `commands.dispatch` | Dispatch Diagnostics Commands | ✓ | ✓ |  |  |
| `reports.view` | Export Analytics & Attendance | ✓ | ✓ | ✓ |  |
| `users.view` | View Portal User Accounts | ✓ |  |  |  |
| `users.manage` | Manage Operator Logins | ✓ |  |  |  |
| `roles.view` | View Roles & Permissions | ✓ |  |  |  |
| `roles.manage` | Create & Modify Roles | ✓ |  |  |  |
| `permissions.view` | Browse Permissions Catalog | ✓ |  | ✓ |  |
| `audit.view` | View Immutable Audit Logs | ✓ |  | ✓ |  |
| `settings.view` | View Portal Settings | ✓ | ✓ |  |  |
| `settings.manage` | Modify System Configuration | ✓ | ✓ |  |  |
