import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '@/api/devices';
import { WorkSession } from '@/types/workforce';
import { DataTable, Column } from '@/components/tables/DataTable';
import { StatusBadge } from '@/components/status/StatusBadge';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import { Timer, Clock, Laptop, RefreshCw } from 'lucide-react';
import { useRealtime } from '@/context/RealtimeContext';

export const WorkSessionsPage: React.FC = () => {
  const { lastDeviceUpdate } = useRealtime();
  const [page, setPage] = useState(1);

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['work-sessions', page],
    queryFn: () => monitoringApi.getSessions({ page, page_size: 15 }),
    refetchInterval: 10000,
  });

  const formatMinutes = (sec: number) => {
    if (!sec || sec <= 0) return '0m';
    const hrs = Math.floor(sec / 3600);
    const mins = Math.floor((sec % 3600) / 60);
    if (hrs > 0) return `${hrs}h ${mins}m`;
    return `${mins}m`;
  };

  const columns: Column<WorkSession>[] = [
    {
      header: 'Employee & User',
      accessor: (row) => (
        <div>
          <span className="font-semibold text-foreground text-sm block">{row.employee_name}</span>
          {row.employee_code && <span className="text-xs text-muted-foreground font-mono">{row.employee_code}</span>}
        </div>
      ),
    },
    {
      header: 'Live State',
      accessor: (row) => <StatusBadge status={row.current_state || 'OFFLINE'} size="sm" />,
    },
    {
      header: 'Workstation',
      accessor: (row) => (
        <span className="text-xs text-muted-foreground flex items-center gap-1.5 font-mono">
          <Laptop className="w-3.5 h-3.5" />
          {row.hostname}
        </span>
      ),
    },
    {
      header: 'Session Date',
      accessor: (row) => <span className="text-xs font-mono text-muted-foreground">{row.session_date}</span>,
    },
    {
      header: 'Session Start',
      accessor: (row) => (
        <span className="text-xs font-mono text-muted-foreground">
          {new Date(row.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
        </span>
      ),
    },
    {
      header: 'Total / Active Duration',
      accessor: (row) => {
        const total = row.calculated_duration_seconds || row.total_duration_seconds || 0;
        return (
          <div className="space-y-0.5">
            <span className="text-xs font-bold text-foreground font-mono block">
              {formatMinutes(total)}
            </span>
            <span className="text-[11px] text-emerald-400 font-mono">
              {formatMinutes(row.active_duration_seconds)} active
            </span>
          </div>
        );
      },
    },
    {
      header: 'Idle Duration',
      accessor: (row) => (
        <span className="text-xs font-mono text-amber-400">
          {formatMinutes(row.idle_duration_seconds)}
        </span>
      ),
    },
    {
      header: 'Session State',
      accessor: (row) => (
        <Badge variant={row.status === 'OPEN' ? 'success' : 'default'} size="sm">
          {row.status === 'OPEN' ? 'IN PROGRESS' : 'CLOSED'}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Active Work Sessions</h1>
          <p className="text-xs text-muted-foreground">
            Granular active vs idle session durations computed continuously per employee endpoint.
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          isLoading={isFetching}
          className="h-9 px-3 gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh</span>
        </Button>
      </div>

      <DataTable
        columns={columns}
        data={data?.items || []}
        isLoading={isLoading}
        page={data?.pagination?.page}
        totalPages={data?.pagination?.total_pages}
        onPageChange={setPage}
        keyExtractor={(row) => row.id}
      />
    </div>
  );
};
