import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '@/api/devices';
import { TelemetryEvent } from '@/types/monitoring';
import { DataTable, Column } from '@/components/tables/DataTable';
import { StatusBadge } from '@/components/status/StatusBadge';
import { Select } from '@/components/common/Select';
import { Laptop, History, RefreshCw } from 'lucide-react';
import { Button } from '@/components/common/Button';

export const EventsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const [eventType, setEventType] = useState('');

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['events', page, eventType],
    queryFn: () => monitoringApi.getEvents({ page, page_size: 20, event_type: eventType || undefined }),
    refetchInterval: 10000,
  });

  const columns: Column<TelemetryEvent>[] = [
    {
      header: 'Event / State',
      accessor: (row) => <StatusBadge status={row.event_type} size="sm" />,
    },
    {
      header: 'Device & Hostname',
      accessor: (row) => (
        <span className="text-xs font-mono text-foreground flex items-center gap-1.5">
          <Laptop className="w-3.5 h-3.5 text-primary" />
          {row.hostname || 'Endpoint'}
        </span>
      ),
    },
    {
      header: 'Employee',
      accessor: (row) => <span className="text-xs text-muted-foreground">{row.employee_name || 'Unassigned'}</span>,
    },
    {
      header: 'Timestamp',
      accessor: (row) => (
        <span className="text-xs font-mono text-muted-foreground">
          {new Date(row.received_at).toLocaleString()}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Inline Filter */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Event History</h1>
          <p className="text-xs text-muted-foreground">
            Immutable log of endpoint state transitions, login/logout, and lifecycle events.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Select
            value={eventType}
            onChange={(e) => setEventType(e.target.value)}
            options={[
              { label: 'All Event Types', value: '' },
              { label: 'ACTIVE', value: 'ACTIVE' },
              { label: 'IDLE', value: 'IDLE' },
              { label: 'LOGIN', value: 'LOGIN' },
              { label: 'LOGOUT', value: 'LOGOUT' },
              { label: 'LOCK', value: 'LOCK' },
              { label: 'UNLOCK', value: 'UNLOCK' },
              { label: 'SLEEP', value: 'SLEEP' },
              { label: 'RESUME', value: 'RESUME' },
              { label: 'OFFLINE', value: 'OFFLINE' },
            ]}
            className="w-48 text-xs"
          />

          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            disabled={isFetching}
            className="h-9 px-3 gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isFetching ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        </div>
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
