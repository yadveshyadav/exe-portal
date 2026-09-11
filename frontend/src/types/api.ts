import { DeviceStatus } from './device';

export interface ApiResponse<T = any> {
  success: boolean;
  data: T;
  message?: string | null;
  errors?: string[];
}

export interface PaginatedResult<T> {
  items: T[];
  pagination: {
    page: number;
    page_size: number;
    total_count: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface DashboardSummary {
  total_employees: number;
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  stale_devices?: number;
  unassigned_devices?: number;
  agent_errors?: number;
  registered_devices?: number;
  active_devices: number;
  idle_devices: number;
  locked_devices: number;
  active_alerts: number;
  live_workforce_breakdown: {
    active: number;
    idle: number;
    offline: number;
    locked: number;
    stale?: number;
  };
}
