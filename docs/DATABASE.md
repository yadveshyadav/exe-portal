# Database Schema Reference (PostgreSQL `exe_portal`)

## Entity Relationship Overview

```text
Company
  ├── Departments
  │     └── Employees (hierarchical manager link)
  ├── Employees
  │     ├── Devices (Assigned Hardware)
  │     ├── User (Login Account)
  │     ├── WorkSessions (Active/Idle durations)
  │     ├── Attendance (Daily check-in/out totals)
  │     └── Events (Telemetry event stream)
  ├── Devices
  │     ├── Agent (Binary & config state)
  │     ├── Events
  │     ├── WorkSessions
  │     ├── Commands
  │     └── Alerts
  ├── Roles (Mapped to Permissions via role_permissions)
  ├── Users (Mapped to Roles via user_roles)
  ├── Policies (Agent configurations and PolicyRules)
  └── AuditLogs (Immutable administrative operations)
```

---

## Key Tables

| Table Name | Description | Key Indexes |
| :--- | :--- | :--- |
| `companies` | Multi-tenant company roots | `code`, `is_active` |
| `departments` | Organizational unit hierarchy | `company_id`, `code`, `is_active` |
| `employees` | Employee profiles and staff details | `employee_code`, `email`, `company_id` |
| `users` | Portal web operators and bcrypt password hashes | `username`, `email`, `company_id` |
| `roles` | Security roles (SuperAdmin, Admin, Auditor) | `company_id`, `code` |
| `permissions` | Granular permission registry | `code`, `module` |
| `devices` | Enrolled Windows workstations | `device_uid`, `hostname`, `status` |
| `agents` | Installed emp_runexe version and heartbeat status | `device_id`, `last_heartbeat` |
| `events` | Immutable telemetry event logs | `received_at`, `event_type`, `device_id` |
| `work_sessions` | Active / Idle duration sessions | `session_date`, `employee_id`, `device_id` |
| `attendance_records`| Daily aggregated attendance | `attendance_date`, `employee_id` |
| `policies` | Agent telemetry and threshold policies | `company_id`, `code` |
| `alerts` | Anomaly and threshold alerts | `status`, `severity`, `triggered_at` |
| `commands` | Safe remote administrative commands | `device_id`, `status` |
| `audit_logs` | Immutable administrative audit trails | `company_id`, `user_id`, `created_at` |
