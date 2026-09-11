import { apiClient } from './client';
import { ApiResponse } from '@/types/api';
import { AuthResponse, LoginCredentials, UserProfile } from '@/types/auth';

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const res = await apiClient.post<ApiResponse<AuthResponse>>('/auth/login', credentials);
    return res.data.data;
  },

  getProfile: async (): Promise<UserProfile> => {
    const res = await apiClient.get<ApiResponse<UserProfile>>('/auth/me');
    return res.data.data;
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
  },
};
