import React from 'react';
import { usePermissions } from '@/hooks/usePermissions';

export interface PermissionGateProps {
  permission?: string;
  permissions?: string[];
  requireAll?: boolean;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const PermissionGate: React.FC<PermissionGateProps> = ({
  permission,
  permissions,
  requireAll = false,
  children,
  fallback = null,
}) => {
  const { can, canAny, canAll, isSuperUser } = usePermissions();

  if (isSuperUser) {
    return <>{children}</>;
  }

  if (permission && !can(permission)) {
    return <>{fallback}</>;
  }

  if (permissions && permissions.length > 0) {
    const granted = requireAll ? canAll(permissions) : canAny(permissions);
    if (!granted) {
      return <>{fallback}</>;
    }
  }

  return <>{children}</>;
};
