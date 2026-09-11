import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { RealtimeProvider } from '@/context/RealtimeContext';
import { AppLayout } from '@/components/layout/AppLayout';
import { LoginPage } from '@/pages/Login';
import { DashboardPage } from '@/pages/Dashboard';
import { EmployeesPage } from '@/pages/Employees';
import { DepartmentsPage } from '@/pages/Departments';
import { DevicesPage } from '@/pages/Devices';
import { AttendancePage } from '@/pages/Attendance';
import { WorkSessionsPage } from '@/pages/WorkSessions';
import { EventsPage } from '@/pages/Events';
import { LoadingState } from '@/components/common/LoadingState';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <LoadingState message="Authenticating session..." />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <RealtimeProvider>
          <BrowserRouter>
            <Routes>
              {/* Public route */}
              <Route path="/login" element={<LoginPage />} />

              {/* Protected Portal Shell */}
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <AppLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<DashboardPage />} />

                {/* Workforce & Hardware */}
                <Route path="workforce/employees" element={<EmployeesPage />} />
                <Route path="workforce/departments" element={<DepartmentsPage />} />
                <Route path="devices/all" element={<DevicesPage />} />

                {/* Sessions, Attendance & Events */}
                <Route path="workforce/attendance" element={<AttendancePage />} />
                <Route path="monitoring/sessions" element={<WorkSessionsPage />} />
                <Route path="monitoring/events" element={<EventsPage />} />

                {/* Fallback */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Route>
            </Routes>
          </BrowserRouter>
        </RealtimeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
