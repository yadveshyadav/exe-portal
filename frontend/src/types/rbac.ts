export interface Permission {
  id: string;
  code: string;
  name: string;
  module: string;
  description?: string;
  created_at: string;
}

export interface Role {
  id: string;
  company_id?: string;
  name: string;
  code: string;
  description?: string;
  is_system: boolean;
  permissions: string[];
  permission_ids?: string[];
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  company_id: string;
  user_id?: string;
  username: string;
  action: string;
  resource_type: string;
  resource_id?: string;
  before_value?: Record<string, any>;
  after_value?: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  result: 'SUCCESS' | 'FAILURE';
  failure_reason?: string;
  created_at: string;
}
