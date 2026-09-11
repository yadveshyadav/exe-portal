import { DeviceStatus } from './device';

export type WebSocketEventType =
  | 'DEVICE_REGISTERED'
  | 'DEVICE_ONLINE'
  | 'DEVICE_OFFLINE'
  | 'DEVICE_STALE'
  | 'HEARTBEAT_RECEIVED'
  | 'AGENT_VERSION_CHANGED'
  | 'DEVICE_STATUS_CHANGED'
  | 'ALERT_TRIGGERED'
  | 'ALERT_RESOLVED'
  | 'COMMAND_STATUS_UPDATED'
  | 'CONFIGURATION_UPDATED'
  | 'WORK_SESSION_UPDATED'
  | 'EVENT_RECORDED';

export interface DeviceStatusChangedPayload {
  device_id: string;
  employee_id?: string;
  status: DeviceStatus;
  hostname?: string;
  agent_version?: string;
  last_seen?: string;
  metadata?: Record<string, any>;
}

export interface WebSocketEventMessage<T = any> {
  type: WebSocketEventType;
  company_id: string;
  timestamp: string;
  data?: T;
  payload?: T;
  device_id?: string;
}
