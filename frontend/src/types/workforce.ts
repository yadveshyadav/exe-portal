export interface Department {
  id: string;
  company_id: string;
  name: string;
  code: string;
  description?: string;
  parent_id?: string;
  manager_id?: string;
  created_at: string;
  is_active: boolean;
}

export interface Employee {
  id: string;
  company_id: string;
  department_id?: string;
  department_name?: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone?: string;
  designation?: string;
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED' | 'TERMINATED';
  avatar_url?: string;
  joined_date?: string;
  created_at: string;
  is_active: boolean;
  devices?: any[];
}

export interface AttendanceRecord {
  id: string;
  company_id: string;
  employee_id: string;
  employee_name: string;
  employee_code?: string;
  department_name?: string;
  device_id?: string;
  hostname?: string;
  os_name?: string;
  current_state?: string;
  attendance_date: string;
  first_check_in?: string;
  last_check_out?: string;
  total_work_seconds: number;
  calculated_duration_seconds?: number;
  status: 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'ON_LEAVE' | string;
  verification_status: string;
  created_at: string;
}

export interface WorkSession {
  id: string;
  company_id: string;
  employee_id: string;
  employee_name: string;
  employee_code?: string;
  device_id: string;
  hostname: string;
  current_state?: string;
  session_date: string;
  start_time: string;
  end_time?: string;
  total_duration_seconds: number;
  calculated_duration_seconds?: number;
  active_duration_seconds: number;
  idle_duration_seconds: number;
  status: 'OPEN' | 'CLOSED';
}
