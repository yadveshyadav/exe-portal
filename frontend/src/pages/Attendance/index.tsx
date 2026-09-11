import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '@/api/devices';
import { AttendanceRecord } from '@/types/workforce';
import { DataTable, Column } from '@/components/tables/DataTable';
import { StatusBadge } from '@/components/status/StatusBadge';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { CalendarCheck, Search, Clock, Calendar, Laptop, RefreshCw, UserCheck, ArrowRight } from 'lucide-react';
import { useRealtime } from '@/context/RealtimeContext';

export const AttendancePage: React.FC = () => {
  const { lastDeviceUpdate } = useRealtime();
  const [page, setPage] = useState(1);
  const [date, setDate] = useState('');
  const [search, setSearch] = useState('');

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['attendance', page, date],
    queryFn: () => monitoringApi.getAttendance({ page, page_size: 15, date: date || undefined }),
    refetchInterval: 10000,
  });

  const formatDuration = (totalSeconds: number) => {
    if (!totalSeconds || totalSeconds <= 0) return '0m';
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    if (hrs > 0) {
      return `${hrs}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const filteredItems = (data?.items || []).filter((row) => {
    if (!search) return true;
    const term = search.toLowerCase();
    return (
      row.employee_name?.toLowerCase().includes(term) ||
      row.employee_code?.toLowerCase().includes(term) ||
      row.hostname?.toLowerCase().includes(term) ||
      row.status?.toLowerCase().includes(term)
    );
  });

  const columns: Column<AttendanceRecord>[] = [
    {
      header: 'Employee & User',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-semibold text-xs">
            {row.employee_name ? row.employee_name.charAt(0).toUpperCase() : 'U'}
          </div>
          <div>
            <span className="font-semibold text-foreground text-sm block">{row.employee_name}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground font-mono">{row.employee_code || 'EMP'}</span>
              {row.department_name && (
                <span className="text-[11px] px-1.5 py-0.2 rounded bg-muted text-muted-foreground">
                  {row.department_name}
                </span>
              )}
            </div>
          </div>
        </div>
      ),
    },
    {
      header: 'Current State',
      accessor: (row) => <StatusBadge status={row.current_state || 'OFFLINE'} size="sm" />,
    },
    {
      header: 'Workstation',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          <Laptop className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
          <div>
            <span className="text-xs font-semibold text-foreground block font-mono">{row.hostname || 'Unassigned'}</span>
            <span className="text-[11px] text-muted-foreground">{row.os_name || 'Windows'}</span>
          </div>
        </div>
      ),
    },
    {
      header: 'Check-in Time',
      accessor: (row) => (
        <div>
          <span className="text-xs font-semibold text-emerald-400 font-mono block">
            {row.first_check_in ? new Date(row.first_check_in).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--'}
          </span>
          <span className="text-[11px] text-muted-foreground font-mono">{row.attendance_date}</span>
        </div>
      ),
    },
    {
      header: 'Check-out Time',
      accessor: (row) => (
        <div>
          {row.current_state === 'ACTIVE' ? (
            <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping inline-block" />
              Active Now
            </span>
          ) : (
            <span className="text-xs text-muted-foreground font-mono block">
              {row.last_check_out ? new Date(row.last_check_out).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--'}
            </span>
          )}
        </div>
      ),
    },
    {
      header: 'Calculated Duration',
      accessor: (row) => {
        const dur = row.calculated_duration_seconds || row.total_work_seconds || 0;
        return (
          <div className="space-y-0.5">
            <div className="flex items-center gap-1 text-xs font-bold text-foreground font-mono">
              <Clock className="w-3.5 h-3.5 text-primary" />
              <span>{formatDuration(dur)}</span>
            </div>
            {row.total_work_seconds > 0 && (
              <span className="text-[11px] text-muted-foreground font-mono block">
                {formatDuration(row.total_work_seconds)} active
              </span>
            )}
          </div>
        );
      },
    },
    {
      header: 'Daily Status',
      accessor: (row) => (
        <Badge
          variant={
            row.status === 'PRESENT'
              ? 'success'
              : row.status === 'HALF_DAY'
              ? 'warning'
              : 'default'
          }
          size="sm"
        >
          {row.status}
        </Badge>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Attendance & Work History</h1>
          <p className="text-xs text-muted-foreground">
            User login history, check-in, check-out, duration, and live workstation states.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Input
            placeholder="Search employee, hostname, code..."
            leftIcon={<Search className="w-4 h-4" />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-56 text-xs h-9"
          />

          <div className="flex items-center gap-1.5">
            <Input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-36 text-xs h-9"
            />
            {date && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDate('')}
                className="h-9 px-2 text-xs text-muted-foreground"
              >
                Clear
              </Button>
            )}
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
      </div>

      {/* Attendance Table */}
      <DataTable
        columns={columns}
        data={filteredItems}
        isLoading={isLoading}
        page={data?.pagination?.page}
        totalPages={data?.pagination?.total_pages}
        onPageChange={setPage}
        keyExtractor={(row) => row.id}
      />
    </div>
  );
};
