export const PERMISSIONS = {
  DASHBOARD_VIEW: 'dashboard.view',
  
  EMPLOYEES_VIEW: 'employees.view',
  EMPLOYEES_CREATE: 'employees.create',
  EMPLOYEES_EDIT: 'employees.edit',
  EMPLOYEES_DEACTIVATE: 'employees.deactivate',

  DEPARTMENTS_VIEW: 'departments.view',
  DEPARTMENTS_MANAGE: 'departments.manage',

  DEVICES_VIEW: 'devices.view',
  DEVICES_MANAGE: 'devices.manage',

  AGENTS_VIEW: 'agents.view',
  AGENTS_MANAGE: 'agents.manage',

  MONITORING_VIEW: 'monitoring.view',
  MONITORING_HISTORY: 'monitoring.history',

  ATTENDANCE_VIEW: 'attendance.view',
  REPORTS_VIEW: 'reports.view',

  POLICIES_VIEW: 'policies.view',
  POLICIES_MANAGE: 'policies.manage',

  ALERTS_VIEW: 'alerts.view',
  ALERTS_MANAGE: 'alerts.manage',

  COMMANDS_VIEW: 'commands.view',
  COMMANDS_DISPATCH: 'commands.dispatch',

  USERS_VIEW: 'users.view',
  USERS_MANAGE: 'users.manage',

  ROLES_VIEW: 'roles.view',
  ROLES_MANAGE: 'roles.manage',

  PERMISSIONS_VIEW: 'permissions.view',

  AUDIT_VIEW: 'audit.view',

  SETTINGS_VIEW: 'settings.view',
  SETTINGS_MANAGE: 'settings.manage',
} as const;

export type PermissionCode = typeof PERMISSIONS[keyof typeof PERMISSIONS];
