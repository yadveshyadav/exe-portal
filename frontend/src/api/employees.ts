import { apiClient } from './client';
import { ApiResponse, PaginatedResult } from '@/types/api';
import { Employee, Department } from '@/types/workforce';

export const employeesApi = {
  list: async (params?: { page?: number; page_size?: number; search?: string; department_id?: string; status?: string }): Promise<PaginatedResult<Employee>> => {
    const res = await apiClient.get<ApiResponse<PaginatedResult<Employee>>>('/employees', { params });
    return res.data.data;
  },

  getById: async (id: string): Promise<Employee> => {
    const res = await apiClient.get<ApiResponse<Employee>>(`/employees/${id}`);
    return res.data.data;
  },

  create: async (data: Partial<Employee>): Promise<Employee> => {
    const res = await apiClient.post<ApiResponse<Employee>>('/employees', data);
    return res.data.data;
  },

  update: async (id: string, data: Partial<Employee>): Promise<Employee> => {
    const res = await apiClient.put<ApiResponse<Employee>>(`/employees/${id}`, data);
    return res.data.data;
  },

  deactivate: async (id: string): Promise<void> => {
    await apiClient.delete(`/employees/${id}`);
  },

  assignDevice: async (employeeId: string, deviceId: string): Promise<Employee> => {
    const res = await apiClient.post<ApiResponse<Employee>>(`/employees/${employeeId}/assign-device`, {
      device_id: deviceId,
    });
    return res.data.data;
  },
};

export const departmentsApi = {
  list: async (): Promise<{ items: Department[] }> => {
    const res = await apiClient.get<ApiResponse<{ items: Department[] }>>('/departments');
    return res.data.data;
  },

  create: async (data: Partial<Department>): Promise<Department> => {
    const res = await apiClient.post<ApiResponse<Department>>('/departments', data);
    return res.data.data;
  },

  update: async (id: string, data: Partial<Department>): Promise<Department> => {
    const res = await apiClient.put<ApiResponse<Department>>(`/departments/${id}`, data);
    return res.data.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/departments/${id}`);
  },
};
