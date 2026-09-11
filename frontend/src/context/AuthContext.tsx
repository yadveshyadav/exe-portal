import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile, LoginCredentials } from '@/types/auth';
import { authApi } from '@/api/auth';
import { realtimeClient } from '@/websocket/client';

interface AuthContextType {
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  hasPermission: (permissionCode: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const profile = await authApi.getProfile();
          setUser(profile);
          localStorage.setItem('user', JSON.stringify(profile));
          // Connect WebSocket with user & company context
          realtimeClient.connect(profile.company_id, profile.id);
        } catch (err) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    setIsLoading(true);
    try {
      const res = await authApi.login(credentials);
      localStorage.setItem('access_token', res.access_token);
      localStorage.setItem('refresh_token', res.refresh_token);
      localStorage.setItem('user', JSON.stringify(res.user));
      setUser(res.user);
      realtimeClient.connect(res.user.company_id, res.user.id);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore network errors on logout
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      setUser(null);
      realtimeClient.disconnect();
    }
  };

  const hasPermission = (permissionCode: string): boolean => {
    if (!user) return false;
    if (user.is_superuser) return true;
    if (user.permissions.includes('*')) return true;
    return user.permissions.includes(permissionCode);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasPermission,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
