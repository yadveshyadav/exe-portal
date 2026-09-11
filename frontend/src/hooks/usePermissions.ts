import { useAuth } from '@/context/AuthContext';

export const usePermissions = () => {
  const { hasPermission, user } = useAuth();

  const can = (permissionCode: string): boolean => {
    return hasPermission(permissionCode);
  };

  const canAny = (permissionCodes: string[]): boolean => {
    return permissionCodes.some((code) => hasPermission(code));
  };

  const canAll = (permissionCodes: string[]): boolean => {
    return permissionCodes.every((code) => hasPermission(code));
  };

  return { can, canAny, canAll, isSuperUser: !!user?.is_superuser };
};
