import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '@/api/devices';
import { useRealtime } from '@/context/RealtimeContext';
import { MetricCard } from '@/components/cards/MetricCard';
import { LiveWorkforceCard } from '@/components/cards/LiveWorkforceCard';
import { EventFeedCard } from '@/components/cards/EventFeedCard';
import { WorkforceActivityChart } from '@/components/charts/WorkforceActivityChart';
import { AttendanceTrendChart } from '@/components/charts/AttendanceTrendChart';
import { LoadingState, ErrorState } from '@/components/common/LoadingState';
import {
  Users,
  Laptop,
  Wifi,
  WifiOff,
  Activity,
  Clock,
  ShieldAlert,
  UserX,
  AlertTriangle,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { lastDeviceUpdate, isConnected } = useRealtime();

  const {
    data: summary,
    isLoading: summaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useQuery({
    queryKey: ['dashboard', 'summary'],
    queryFn: dashboardApi.getSummary,
    refetchInterval: 10000,
  });

  const {
    data: eventsData,
    isLoading: eventsLoading,
  } = useQuery({
    queryKey: ['dashboard', 'recent-events'],
    queryFn: dashboardApi.getRecentEvents,
    refetchInterval: 10000,
  });

  if (summaryLoading) {
    return <LoadingState message="Loading enterprise telemetry overview..." />;
  }

  if (summaryError || !summary) {
    return (
      <ErrorState
        title="Failed to load dashboard metrics"
        message="Could not retrieve real-time summary from the backend API."
        onRetry={refetchSummary}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Dashboard</h1>
          <p className="text-xs text-muted-foreground">
            Real-time workforce activity, endpoint telemetry, and Windows agent operations.
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground bg-card px-3 py-1.5 rounded-lg border border-border">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-zinc-500'}`} />
          <span>{isConnected ? 'Live WebSocket Connected' : 'Connecting to WebSocket...'}</span>
        </div>
      </div>

      {/* Top 6 Device Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <MetricCard
          title="Total Devices"
          value={summary.total_devices}
          subtitle="Enrolled PCs"
          icon={<Laptop className="w-4 h-4" />}
          color="blue"
        />
        <MetricCard
          title="Online Devices"
          value={summary.online_devices}
          subtitle="Active heartbeats"
          icon={<Wifi className="w-4 h-4" />}
          color="emerald"
        />
        <MetricCard
          title="Offline Devices"
          value={summary.offline_devices}
          subtitle="No heartbeat >120s"
          icon={<WifiOff className="w-4 h-4" />}
          color="zinc"
        />
        <MetricCard
          title="Stale Devices"
          value={summary.stale_devices ?? 0}
          subtitle="Missed >60s"
          icon={<Clock className="w-4 h-4" />}
          color="amber"
        />
        <MetricCard
          title="Unassigned"
          value={summary.unassigned_devices ?? 0}
          subtitle="Needs employee"
          icon={<UserX className="w-4 h-4" />}
          color="purple"
        />
        <MetricCard
          title="Agent Issues"
          value={summary.agent_errors ?? 0}
          subtitle="Errors / Outdated"
          icon={<AlertTriangle className="w-4 h-4" />}
          color="rose"
        />
      </div>

      {/* Middle Grid: Live Workforce Breakdown + Recent Telemetry Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7">
          <LiveWorkforceCard
            breakdown={summary.live_workforce_breakdown}
            totalDevices={summary.total_devices}
          />
        </div>
        <div className="lg:col-span-5">
          <EventFeedCard events={eventsData?.events || []} />
        </div>
      </div>

      {/* Bottom Grid: Hourly Activity Chart + 7-Day Attendance Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <WorkforceActivityChart />
        <AttendanceTrendChart />
      </div>
    </div>
  );
};
