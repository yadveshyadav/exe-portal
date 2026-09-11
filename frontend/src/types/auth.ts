export interface UserProfile {
  id: string;
  company_id: string;
  employee_id?: string;
  username: string;
  email: string;
  is_superuser: boolean;
  status: 'ACTIVE' | 'DISABLED' | 'LOCKED';
  last_login?: string;
  roles: string[];
  permissions: string[];
  full_name: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: UserProfile;
}

export interface LoginCredentials {
  username_or_email: string;
  password: string;
}
