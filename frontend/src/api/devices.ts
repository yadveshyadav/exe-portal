import { apiClient } from './client';
import { ApiResponse, PaginatedResult, DashboardSummary } from '@/types/api';
import { Device, DeviceDetail } from '@/types/device';
import { TelemetryEvent } from '@/types/monitoring';
import { AttendanceRecord, WorkSession } from '@/types/workforce';

export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const res = await apiClient.get<ApiResponse<DashboardSummary>>('/dashboard/summary');
    return res.data.data;
  },
  getRecentEvents: async (): Promise<{ events: TelemetryEvent[] }> => {
    const res = await apiClient.get<ApiResponse<{ events: TelemetryEvent[] }>>('/dashboard/recent-events');
    return res.data.data;
  },
};

export const devicesApi = {
  list: async (params?: {
    page?: number;
    page_size?: number;
    status?: string;
    search?: string;
    unassigned?: boolean;
    employee_id?: string;
    department_id?: string;
    agent_version?: string;
  }): Promise<PaginatedResult<Device>> => {
    const res = await apiClient.get<ApiResponse<PaginatedResult<Device>>>('/devices', { params });
    return res.data.data;
  },
  getById: async (id: string): Promise<DeviceDetail> => {
    const res = await apiClient.get<ApiResponse<DeviceDetail>>(`/devices/${id}`);
    return res.data.data;
  },
  update: async (id: string, data: Partial<Device>): Promise<Device> => {
    const res = await apiClient.put<ApiResponse<Device>>(`/devices/${id}`, data);
    return res.data.data;
  },
  assignEmployee: async (deviceId: string, employeeId: string | null): Promise<Device> => {
    const res = await apiClient.post<ApiResponse<Device>>(`/devices/${deviceId}/assign`, {
      employee_id: employeeId,
    });
    return res.data.data;
  },
  unassignEmployee: async (deviceId: string): Promise<Device> => {
    const res = await apiClient.post<ApiResponse<Device>>(`/devices/${deviceId}/unassign`);
    return res.data.data;
  },
  disableDevice: async (deviceId: string): Promise<Device> => {
    const res = await apiClient.post<ApiResponse<Device>>(`/devices/${deviceId}/disable`);
    return res.data.data;
  },
  enableDevice: async (deviceId: string): Promise<Device> => {
    const res = await apiClient.post<ApiResponse<Device>>(`/devices/${deviceId}/enable`);
    return res.data.data;
  },
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/devices/${id}`);
  },
};

export const monitoringApi = {
  getEvents: async (params?: { page?: number; page_size?: number; event_type?: string; device_id?: string; employee_id?: string }): Promise<PaginatedResult<TelemetryEvent>> => {
    const res = await apiClient.get<ApiResponse<PaginatedResult<TelemetryEvent>>>('/events', { params });
    return res.data.data;
  },
  getAttendance: async (params?: { page?: number; page_size?: number; date?: string; employee_id?: string }): Promise<PaginatedResult<AttendanceRecord>> => {
    const res = await apiClient.get<ApiResponse<PaginatedResult<AttendanceRecord>>>('/attendance', { params });
    return res.data.data;
  },
  getSessions: async (params?: { page?: number; page_size?: number; employee_id?: string; device_id?: string }): Promise<PaginatedResult<WorkSession>> => {
    const res = await apiClient.get<ApiResponse<PaginatedResult<WorkSession>>>('/sessions', { params });
    return res.data.data;
  },
};

export interface AgentConfig {
  server_url?: string;
  server_ip?: string;
  server_port?: number;
  heartbeat_interval_seconds?: number;
  idle_threshold_seconds?: number;
  reconnect_interval_seconds?: number;
  event_batch_size?: number;
  log_retention_days?: number;
}

export const agentsApi = {
  getConfig: async (deviceId?: string): Promise<{ configuration: AgentConfig }> => {
    const url = deviceId ? `/agents/${deviceId}/config` : '/agents/config';
    const res = await apiClient.get<ApiResponse<{ configuration: AgentConfig }>>(url);
    return res.data.data;
  },
  pushConfig: async (deviceId: string, config: AgentConfig): Promise<{ status: string; configuration: AgentConfig }> => {
    const url = deviceId === 'global' ? '/agents/config' : `/agents/${deviceId}/config`;
    const res = await apiClient.post<ApiResponse<{ status: string; configuration: AgentConfig }>>(url, config);
    return res.data.data;
  },
};
