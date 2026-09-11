import { DeviceStatus } from './device';

export interface LiveMonitoringRow {
  device_id: string;
  device_uid: string;
  hostname: string;
  employee_id?: string;
  employee_name: string;
  employee_code: string;
  department_name: string;
  status: DeviceStatus;
  work_state: string;
  last_seen?: string;
  session_duration_seconds: number;
  active_duration_seconds: number;
  idle_duration_seconds: number;
  agent_version: string;
  ip_address: string;
}

export interface TelemetryEvent {
  id: string;
  company_id: string;
  device_id: string;
  employee_id?: string;
  hostname?: string;
  employee_name?: string;
  event_type: string;
  event_timestamp: string;
  received_at: string;
  severity: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  metadata_payload: Record<string, any>;
}

export interface AlertItem {
  id: string;
  company_id: string;
  device_id?: string;
  employee_id?: string;
  hostname?: string;
  employee_name?: string;
  alert_type: string;
  title: string;
  description?: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'TRIGGERED' | 'ACKNOWLEDGED' | 'RESOLVED' | 'DISMISSED';
  triggered_at: string;
  resolved_at?: string;
  resolved_by?: string;
  resolution_notes?: string;
}

export interface CommandItem {
  id: string;
  company_id: string;
  device_id: string;
  hostname?: string;
  command_type: 'SYNC' | 'REFRESH_CONFIGURATION' | 'HEALTH_CHECK' | 'CHECK_VERSION';
  parameters: Record<string, any>;
  status: 'PENDING' | 'SENT' | 'DELIVERED' | 'EXECUTED' | 'FAILED' | 'TIMED_OUT';
  created_by?: string;
  created_at: string;
  executed_at?: string;
  result?: {
    exit_code: number;
    result_payload: Record<string, any>;
    error_message?: string;
  };
}

export interface PolicyRule {
  id?: string;
  rule_type: string;
  rule_value: Record<string, any>;
}

export interface PolicyItem {
  id: string;
  company_id: string;
  name: string;
  code: string;
  description?: string;
  is_default: boolean;
  version: string;
  priority: number;
  created_at: string;
  rules?: PolicyRule[];
}
