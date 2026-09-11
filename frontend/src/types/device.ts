export type DeviceStatus =
  | 'REGISTERED'
  | 'ONLINE'
  | 'STALE'
  | 'OFFLINE'
  | 'DISABLED'
  | 'ERROR'
  | 'ACTIVE'
  | 'IDLE'
  | 'LOCKED'
  | 'UNKNOWN';

export interface Device {
  id: string;
  device_id: string;
  device_uuid: string;
  device_uid: string;
  company_id: string;
  employee_id?: string | null;
  employee_name?: string;
  employee_code?: string;
  hostname: string;
  operating_system: string;
  os_name?: string;
  os_version?: string;
  os_architecture?: string;
  agent_version: string;
  status: DeviceStatus;
  last_ip?: string;
  ip_address?: string;
  mac_address?: string;
  city?: string | null;
  region?: string | null;
  country?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string | null;
  isp?: string | null;
  location_formatted?: string | null;
  last_seen?: string | null;
  last_seen_at?: string | null;
  registered_at: string;
  created_at: string;
  is_enrolled: boolean;
  is_active: boolean;
}

export interface AgentInfo {
  id: string;
  device_id: string;
  version: string;
  build_number?: string;
  agent_status: 'RUNNING' | 'STOPPED' | 'ERROR' | 'OUTDATED';
  last_heartbeat?: string;
  config_version: string;
  config_hash?: string;
}

export interface AuditLogEntry {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  username: string;
  before_value?: any;
  after_value?: any;
  ip_address?: string;
  result: string;
  created_at: string;
}

export interface DeviceDetail extends Device {
  agent?: AgentInfo;
  employee?: {
    id: string;
    employee_code: string;
    first_name: string;
    last_name: string;
    full_name: string;
    email: string;
    designation?: string;
    department_name?: string;
  } | null;
  live_state?: {
    device_id: string;
    status: DeviceStatus;
    last_seen: string;
    hostname?: string;
    agent_version?: string;
    ip_address?: string;
  } | null;
  websocket_status?: 'CONNECTED' | 'DISCONNECTED';
  recent_events?: any[];
  recent_sessions?: any[];
  audit_history?: AuditLogEntry[];
}
