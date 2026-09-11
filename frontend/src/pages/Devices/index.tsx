import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { devicesApi, agentsApi, AgentConfig } from '@/api/devices';
import { employeesApi } from '@/api/employees';
import { Device, DeviceDetail, DeviceStatus } from '@/types/device';
import { Employee } from '@/types/workforce';
import { DataTable, Column } from '@/components/tables/DataTable';
import { StatusBadge } from '@/components/status/StatusBadge';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Modal } from '@/components/modals/Modal';
import {
  Laptop,
  Search,
  RefreshCw,
  Settings,
  Server,
  CheckCircle2,
  Send,
  UserCheck,
  UserX,
  ShieldBan,
  ShieldCheck,
  Eye,
  Activity,
  Radio,
  Clock,
  History,
  FileText,
  Copy,
  Check,
  AlertTriangle,
  User,
  Info,
  MapPin,
  Globe,
  Navigation
} from 'lucide-react';
import { useRealtime } from '@/context/RealtimeContext';
import { clsx } from 'clsx';

type FilterTab = 'ALL' | 'ONLINE' | 'OFFLINE' | 'UNASSIGNED' | 'DISABLED' | 'AGENT_ISSUES';

export const DevicesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { lastDeviceUpdate, isConnected } = useRealtime();

  const [activeTab, setActiveTab] = useState<FilterTab>('ALL');
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Modals state
  const [selectedDevice, setSelectedDevice] = useState<DeviceDetail | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [detailTab, setDetailTab] = useState<'overview' | 'employee' | 'agent' | 'events' | 'history' | 'audit'>('overview');

  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [deviceToAssign, setDeviceToAssign] = useState<Device | null>(null);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<string>('');

  const [disableModalOpen, setDisableModalOpen] = useState(false);
  const [deviceToToggle, setDeviceToToggle] = useState<Device | null>(null);

  // Config modal
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [targetDeviceId, setTargetDeviceId] = useState<string | null>(null);
  const [serverIp, setServerIp] = useState('192.168.1.253');
  const [serverPort, setServerPort] = useState('5000');
  const [heartbeatSec, setHeartbeatSec] = useState('30');
  const [idleSec, setIdleSec] = useState('300');
  const [pushSuccess, setPushSuccess] = useState<string | null>(null);
  const [isPushing, setIsPushing] = useState(false);

  // Query devices
  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['devices', page, search, activeTab],
    queryFn: () =>
      devicesApi.list({
        page,
        page_size: 15,
        status: activeTab === 'ALL' ? undefined : activeTab,
        search: search || undefined,
      }),
    refetchInterval: 10000,
  });

  // Query employees for assignment modal
  const { data: employeesData } = useQuery({
    queryKey: ['employees', 'list-for-assign'],
    queryFn: () => employeesApi.list({ page_size: 100, status: 'ACTIVE' }),
    enabled: assignModalOpen,
  });

  // Realtime cache invalidation on updates
  useEffect(() => {
    if (lastDeviceUpdate) {
      refetch();
    }
  }, [lastDeviceUpdate, refetch]);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleOpenDetail = async (device: Device) => {
    try {
      const detail = await devicesApi.getById(device.id);
      setSelectedDevice(detail);
      setDetailTab('overview');
      setDetailModalOpen(true);
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to load device details');
    }
  };

  const handleOpenAssignModal = (device: Device) => {
    setDeviceToAssign(device);
    setSelectedEmployeeId(device.employee_id || '');
    setAssignModalOpen(true);
  };

  const handleAssignEmployee = async () => {
    if (!deviceToAssign) return;
    try {
      if (selectedEmployeeId) {
        await devicesApi.assignEmployee(deviceToAssign.id, selectedEmployeeId);
      } else {
        await devicesApi.unassignEmployee(deviceToAssign.id);
      }
      setAssignModalOpen(false);
      setDeviceToAssign(null);
      queryClient.invalidateQueries({ queryKey: ['devices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to update employee assignment');
    }
  };

  const handleToggleDeviceStatus = async () => {
    if (!deviceToToggle) return;
    try {
      if (deviceToToggle.status === 'DISABLED') {
        await devicesApi.enableDevice(deviceToToggle.id);
      } else {
        await devicesApi.disableDevice(deviceToToggle.id);
      }
      setDisableModalOpen(false);
      setDeviceToToggle(null);
      queryClient.invalidateQueries({ queryKey: ['devices'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to update device status');
    }
  };

  const openConfigModal = async (deviceId?: string) => {
    setTargetDeviceId(deviceId || null);
    setPushSuccess(null);
    try {
      const res = await agentsApi.getConfig(deviceId);
      if (res?.configuration) {
        const c = res.configuration;
        if (c.server_ip) setServerIp(c.server_ip);
        if (c.server_port) setServerPort(c.server_port.toString());
        if (c.heartbeat_interval_seconds) setHeartbeatSec(c.heartbeat_interval_seconds.toString());
        if (c.idle_threshold_seconds) setIdleSec(c.idle_threshold_seconds.toString());
      }
    } catch {
      // Keep defaults
    }
    setConfigModalOpen(true);
  };

  const handlePushConfig = async (isGlobal = false) => {
    try {
      setIsPushing(true);
      setPushSuccess(null);
      const url = `http://${serverIp.trim()}:${serverPort.trim()}`;
      await agentsApi.pushConfig(isGlobal || !targetDeviceId ? 'global' : targetDeviceId, {
        server_ip: serverIp.trim(),
        server_port: parseInt(serverPort, 10),
        server_url: url,
        heartbeat_interval_seconds: parseInt(heartbeatSec, 10),
        idle_threshold_seconds: parseInt(idleSec, 10),
      });
      setPushSuccess(isGlobal ? 'Global configuration pushed to all agents!' : 'Configuration dispatched to agent successfully!');
      setTimeout(() => setPushSuccess(null), 4000);
    } catch (err: any) {
      alert(err?.response?.data?.message || 'Failed to dispatch configuration');
    } finally {
      setIsPushing(false);
    }
  };

  const tabs: { id: FilterTab; label: string; count?: number }[] = [
    { id: 'ALL', label: 'All Devices' },
    { id: 'ONLINE', label: 'Online' },
    { id: 'OFFLINE', label: 'Offline' },
    { id: 'UNASSIGNED', label: 'Unassigned' },
    { id: 'DISABLED', label: 'Disabled' },
    { id: 'AGENT_ISSUES', label: 'Agent Issues' },
  ];

  const columns: Column<Device>[] = [
    {
      header: 'Device & Machine ID',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary flex-shrink-0">
            <Laptop className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-semibold text-foreground text-sm block">{row.hostname}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  copyToClipboard(row.device_uuid, `uuid-${row.id}`);
                }}
                className="text-muted-foreground hover:text-foreground transition-colors p-0.5"
                title="Copy Device UUID"
              >
                {copiedId === `uuid-${row.id}` ? (
                  <Check className="w-3 h-3 text-emerald-400" />
                ) : (
                  <Copy className="w-3 h-3" />
                )}
              </button>
            </div>
            <span className="text-xs text-muted-foreground font-mono">{row.device_uuid}</span>
          </div>
        </div>
      ),
    },
    {
      header: 'Assigned Employee',
      accessor: (row) => (
        <div>
          {row.employee_name && row.employee_name !== 'Unassigned' ? (
            <div>
              <span className="text-xs font-medium text-foreground block flex items-center gap-1">
                <User className="w-3 h-3 text-primary" />
                {row.employee_name}
              </span>
              {row.employee_code && (
                <span className="text-[11px] text-muted-foreground font-mono pl-4">{row.employee_code}</span>
              )}
            </div>
          ) : (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium bg-muted/60 text-muted-foreground border border-border">
              Unassigned
            </span>
          )}
        </div>
      ),
    },
    {
      header: 'OS & Agent',
      accessor: (row) => (
        <div>
          <span className="text-xs text-foreground block">{row.operating_system}</span>
          <span className="text-[11px] text-muted-foreground font-mono">v{row.agent_version}</span>
        </div>
      ),
    },
    {
      header: 'Live Status',
      accessor: (row) => <StatusBadge status={row.status} size="sm" />,
    },
    {
      header: 'Last Seen & IP',
      accessor: (row) => (
        <div>
          <span className="text-xs text-muted-foreground font-mono block">
            {row.last_seen ? new Date(row.last_seen).toLocaleTimeString() : 'Never'}
          </span>
          <span className="text-[11px] text-muted-foreground font-mono">{row.last_ip || 'No IP'}</span>
        </div>
      ),
    },
    {
      header: 'Location',
      accessor: (row) => (
        <div className="flex items-center gap-1.5">
          <MapPin className="w-3.5 h-3.5 text-primary flex-shrink-0" />
          {row.location_formatted ? (
            <div>
              <span className="text-xs text-foreground font-medium block">
                {row.city ? `${row.city}, ` : ''}{row.country || row.region}
              </span>
              {row.latitude && row.longitude && (
                <a
                  href={`https://www.google.com/maps?q=${row.latitude},${row.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="text-[10px] text-primary hover:underline font-mono"
                >
                  {row.latitude.toFixed(2)}, {row.longitude.toFixed(2)}
                </a>
              )}
            </div>
          ) : (
            <span className="text-[11px] text-muted-foreground">Local / Unset</span>
          )}
        </div>
      ),
    },
    {
      header: 'Actions',
      accessor: (row) => (
        <div className="flex items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleOpenDetail(row)}
            className="h-7 text-xs px-2 gap-1"
            title="View Details"
          >
            <Eye className="w-3.5 h-3.5 text-primary" />
            <span>Details</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => handleOpenAssignModal(row)}
            className="h-7 text-xs px-2 gap-1"
            title="Assign / Unassign Employee"
          >
            {row.employee_id ? (
              <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
            ) : (
              <UserX className="w-3.5 h-3.5 text-amber-400" />
            )}
            <span>Assign</span>
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setDeviceToToggle(row);
              setDisableModalOpen(true);
            }}
            className={clsx(
              'h-7 text-xs px-2 gap-1',
              row.status === 'DISABLED' ? 'text-emerald-400 border-emerald-500/30' : 'text-rose-400 border-rose-500/30'
            )}
            title={row.status === 'DISABLED' ? 'Enable Device' : 'Disable Device'}
          >
            {row.status === 'DISABLED' ? (
              <ShieldCheck className="w-3.5 h-3.5" />
            ) : (
              <ShieldBan className="w-3.5 h-3.5" />
            )}
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => openConfigModal(row.id)}
            className="h-7 text-xs px-2 gap-1"
            title="Remote Config"
          >
            <Settings className="w-3.5 h-3.5 text-muted-foreground" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Device Management</h1>
            <div className="flex items-center gap-1.5 text-[11px] font-mono px-2 py-0.5 rounded-full bg-card border border-border">
              <span className={clsx('w-2 h-2 rounded-full', isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500')} />
              <span className="text-muted-foreground">{isConnected ? 'Live WebSocket' : 'Offline WS'}</span>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Real-time enrollment, live state, and configuration for Windows emp_runexe workstations.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Input
            placeholder="Search hostname, UUID, IP, employee..."
            leftIcon={<Search className="w-4 h-4" />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-64 text-xs h-9"
          />

          <Button
            variant="outline"
            size="sm"
            onClick={() => openConfigModal()}
            className="h-9 px-3 gap-1.5"
          >
            <Server className="w-3.5 h-3.5 text-primary" />
            <span>Server Settings</span>
          </Button>

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

      {/* Tabs Filter Navigation */}
      <div className="flex items-center gap-1 border-b border-border pb-1 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => {
              setActiveTab(tab.id);
              setPage(1);
            }}
            className={clsx(
              'px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap',
              activeTab === tab.id
                ? 'bg-primary/10 text-primary border border-primary/20 font-semibold'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted/40'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Devices Data Table */}
      <DataTable
        columns={columns}
        data={data?.items || []}
        isLoading={isLoading}
        page={data?.pagination?.page}
        totalPages={data?.pagination?.total_pages}
        onPageChange={setPage}
        onRowClick={handleOpenDetail}
        keyExtractor={(row) => row.id}
      />

      {/* Multi-Tab Comprehensive Device Details Modal */}
      {selectedDevice && (
        <Modal
          isOpen={detailModalOpen}
          onClose={() => setDetailModalOpen(false)}
          title={`Workstation: ${selectedDevice.hostname}`}
          description={`Hardware UID: ${selectedDevice.device_uuid}`}
          maxWidth="2xl"
        >
          <div className="space-y-4 text-xs">
            {/* Modal Tabs Header */}
            <div className="flex items-center gap-1 border-b border-border pb-2">
              {[
                { id: 'overview', label: 'Overview', icon: Info },
                { id: 'employee', label: 'Employee', icon: User },
                { id: 'agent', label: 'Agent & Config', icon: Settings },
                { id: 'events', label: 'Live Events', icon: Activity },
                { id: 'history', label: 'Work Sessions', icon: History },
                { id: 'audit', label: 'Audit Trail', icon: FileText },
              ].map((t) => {
                const Icon = t.icon;
                return (
                  <button
                    key={t.id}
                    onClick={() => setDetailTab(t.id as any)}
                    className={clsx(
                      'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors',
                      detailTab === t.id
                        ? 'bg-primary/10 text-primary border border-primary/20 font-semibold'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted/30'
                    )}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{t.label}</span>
                  </button>
                );
              })}
            </div>

            {/* TAB: Overview */}
            {detailTab === 'overview' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between p-4 bg-muted/30 rounded-xl border border-border">
                  <div>
                    <span className="text-muted-foreground block mb-1">Live Endpoint Status</span>
                    <StatusBadge status={selectedDevice.status} size="md" />
                  </div>
                  <div className="text-right">
                    <span className="text-muted-foreground block mb-1">WebSocket Link</span>
                    <span
                      className={clsx(
                        'inline-flex items-center gap-1 font-mono font-semibold text-xs',
                        selectedDevice.websocket_status === 'CONNECTED' ? 'text-emerald-400' : 'text-zinc-400'
                      )}
                    >
                      <span
                        className={clsx(
                          'w-2 h-2 rounded-full',
                          selectedDevice.websocket_status === 'CONNECTED' ? 'bg-emerald-500 animate-ping' : 'bg-zinc-500'
                        )}
                      />
                      {selectedDevice.websocket_status || 'DISCONNECTED'}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-muted/30 rounded-lg border border-border">
                    <span className="text-muted-foreground block mb-1">Operating System</span>
                    <span className="font-semibold text-foreground block">{selectedDevice.operating_system}</span>
                    <span className="text-muted-foreground font-mono">{selectedDevice.os_architecture || 'x64'}</span>
                  </div>
                  <div className="p-3 bg-muted/30 rounded-lg border border-border">
                    <span className="text-muted-foreground block mb-1">Network & IP</span>
                    <span className="font-mono font-semibold text-foreground block">{selectedDevice.last_ip || 'Unknown'}</span>
                    <span className="text-muted-foreground font-mono">{selectedDevice.mac_address || 'No MAC'}</span>
                  </div>
                  <div className="p-3 bg-muted/30 rounded-lg border border-border">
                    <span className="text-muted-foreground block mb-1">Initial Registration</span>
                    <span className="font-mono text-foreground">
                      {selectedDevice.registered_at ? new Date(selectedDevice.registered_at).toLocaleString() : 'N/A'}
                    </span>
                  </div>
                  <div className="p-3 bg-muted/30 rounded-lg border border-border">
                    <span className="text-muted-foreground block mb-1">Last Heartbeat</span>
                    <span className="font-mono text-foreground font-semibold">
                      {selectedDevice.last_seen ? new Date(selectedDevice.last_seen).toLocaleString() : 'Never'}
                    </span>
                  </div>
                </div>

                {/* Geographic Location Card */}
                <div className="p-3.5 bg-muted/30 rounded-lg border border-border space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-primary" />
                      <span className="font-semibold text-foreground">Geographic Location</span>
                    </div>
                    {selectedDevice.latitude && selectedDevice.longitude && (
                      <a
                        href={`https://www.google.com/maps?q=${selectedDevice.latitude},${selectedDevice.longitude}`}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-primary hover:underline text-xs"
                      >
                        <Globe className="w-3 h-3" />
                        <span>Open in Google Maps</span>
                      </a>
                    )}
                  </div>
                  <div className="grid grid-cols-3 gap-2 text-xs pt-1">
                    <div>
                      <span className="text-muted-foreground block text-[11px]">City / Region</span>
                      <span className="text-foreground font-medium">
                        {selectedDevice.city || selectedDevice.region || 'Local / Unknown'}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[11px]">Country</span>
                      <span className="text-foreground font-medium">
                        {selectedDevice.country || 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block text-[11px]">Coordinates & Timezone</span>
                      <span className="text-foreground font-mono text-[11px]">
                        {selectedDevice.latitude && selectedDevice.longitude
                          ? `${selectedDevice.latitude.toFixed(2)}, ${selectedDevice.longitude.toFixed(2)}`
                          : selectedDevice.timezone || 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB: Employee */}
            {detailTab === 'employee' && (
              <div className="space-y-3">
                {selectedDevice.employee ? (
                  <div className="p-4 bg-muted/30 rounded-xl border border-border space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold">
                          {selectedDevice.employee.first_name?.[0] || 'U'}
                        </div>
                        <div>
                          <span className="font-semibold text-foreground text-sm block">
                            {selectedDevice.employee.full_name}
                          </span>
                          <span className="text-muted-foreground font-mono">{selectedDevice.employee.employee_code}</span>
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setDetailModalOpen(false);
                          handleOpenAssignModal(selectedDevice);
                        }}
                      >
                        Change Assignment
                      </Button>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-2 border-t border-border/50 text-xs">
                      <div>
                        <span className="text-muted-foreground block">Email</span>
                        <span className="text-foreground font-mono">{selectedDevice.employee.email}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground block">Department</span>
                        <span className="text-foreground">{selectedDevice.employee.department_name || 'General'}</span>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 bg-muted/20 rounded-xl border border-dashed border-border text-center space-y-3">
                    <UserX className="w-8 h-8 text-muted-foreground mx-auto" />
                    <div>
                      <span className="font-semibold text-foreground block">No Employee Assigned</span>
                      <p className="text-muted-foreground text-xs">
                        This workstation is currently operating as an unassigned endpoint.
                      </p>
                    </div>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        setDetailModalOpen(false);
                        handleOpenAssignModal(selectedDevice);
                      }}
                    >
                      Assign an Employee
                    </Button>
                  </div>
                )}
              </div>
            )}

            {/* TAB: Agent */}
            {detailTab === 'agent' && (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-muted/30 rounded-lg border border-border">
                    <span className="text-muted-foreground block mb-1">Agent Version</span>
                    <span className="font-mono font-semibold text-foreground text-sm">
                      v{selectedDevice.agent_version || selectedDevice.agent?.version || '1.0.0'}
                    </span>
                  </div>
                  <div className="p-3 bg-muted/30 rounded-lg border border-border">
                    <span className="text-muted-foreground block mb-1">Agent Status</span>
                    <span className="font-mono font-semibold text-emerald-400">
                      {selectedDevice.agent?.agent_status || 'RUNNING'}
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-muted/30 rounded-lg border border-border flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-foreground block">Remote Agent Configuration</span>
                    <span className="text-muted-foreground text-[11px]">
                      Change the destination backend IP, port, and heartbeat intervals.
                    </span>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setDetailModalOpen(false);
                      openConfigModal(selectedDevice.id);
                    }}
                    className="gap-1"
                  >
                    <Settings className="w-3.5 h-3.5 text-primary" />
                    <span>Config</span>
                  </Button>
                </div>
              </div>
            )}

            {/* TAB: Events */}
            {detailTab === 'events' && (
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {selectedDevice.recent_events && selectedDevice.recent_events.length > 0 ? (
                  selectedDevice.recent_events.map((e: any, idx: number) => (
                    <div
                      key={e.id || idx}
                      className="p-2.5 bg-muted/30 rounded-lg border border-border flex items-center justify-between"
                    >
                      <div className="flex items-center gap-2">
                        <StatusBadge status={e.event_type} size="sm" showPulse={false} />
                        <span className="text-foreground font-mono text-xs">{e.event_type}</span>
                      </div>
                      <span className="text-muted-foreground font-mono text-[11px]">
                        {e.event_timestamp ? new Date(e.event_timestamp).toLocaleTimeString() : 'Recent'}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-center py-4">No recent events recorded.</p>
                )}
              </div>
            )}

            {/* TAB: History */}
            {detailTab === 'history' && (
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {selectedDevice.recent_sessions && selectedDevice.recent_sessions.length > 0 ? (
                  selectedDevice.recent_sessions.map((s: any, idx: number) => (
                    <div
                      key={s.id || idx}
                      className="p-2.5 bg-muted/30 rounded-lg border border-border flex items-center justify-between"
                    >
                      <div>
                        <span className="font-semibold text-foreground block">Session {s.session_date}</span>
                        <span className="text-muted-foreground text-[11px]">
                          Active: {Math.round(s.active_duration_seconds / 60)}m | Idle: {Math.round(s.idle_duration_seconds / 60)}m
                        </span>
                      </div>
                      <StatusBadge status={s.status} size="sm" showPulse={false} />
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-center py-4">No historical sessions found.</p>
                )}
              </div>
            )}

            {/* TAB: Audit Trail */}
            {detailTab === 'audit' && (
              <div className="space-y-2 max-h-72 overflow-y-auto">
                {selectedDevice.audit_history && selectedDevice.audit_history.length > 0 ? (
                  selectedDevice.audit_history.map((log) => (
                    <div
                      key={log.id}
                      className="p-2.5 bg-muted/30 rounded-lg border border-border flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-semibold text-foreground block">{log.action}</span>
                        <span className="text-muted-foreground text-[11px]">Actor: {log.username}</span>
                      </div>
                      <span className="text-muted-foreground font-mono text-[11px]">
                        {new Date(log.created_at).toLocaleString()}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground text-center py-4">No audit records found for this device.</p>
                )}
              </div>
            )}
          </div>
        </Modal>
      )}

      {/* Assign Employee Modal */}
      <Modal
        isOpen={assignModalOpen}
        onClose={() => {
          setAssignModalOpen(false);
          setDeviceToAssign(null);
        }}
        title={`Assign Employee to ${deviceToAssign?.hostname}`}
        description="Select an employee from your organization to associate with this workstation."
        maxWidth="md"
      >
        <div className="space-y-4 text-xs">
          <div className="space-y-2">
            <label className="text-xs font-medium text-foreground block">Select Employee</label>
            <select
              value={selectedEmployeeId}
              onChange={(e) => setSelectedEmployeeId(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-3 py-2 text-foreground text-xs focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="">-- Unassigned (No Employee) --</option>
              {employeesData?.items?.map((emp: Employee) => (
                <option key={emp.id} value={emp.id}>
                  {emp.full_name} ({emp.employee_code}) - {emp.department_name || 'General'}
                </option>
              ))}
            </select>
          </div>

          <div className="flex justify-end gap-2 pt-3 border-t border-border">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setAssignModalOpen(false);
                setDeviceToAssign(null);
              }}
            >
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleAssignEmployee}>
              Save Assignment
            </Button>
          </div>
        </div>
      </Modal>

      {/* Disable / Enable Confirmation Modal */}
      <Modal
        isOpen={disableModalOpen}
        onClose={() => {
          setDisableModalOpen(false);
          setDeviceToToggle(null);
        }}
        title={deviceToToggle?.status === 'DISABLED' ? 'Re-enable Workstation' : 'Disable Workstation'}
        description={
          deviceToToggle?.status === 'DISABLED'
            ? `Allow ${deviceToToggle?.hostname} to reconnect and send heartbeats to the portal.`
            : `Disable ${deviceToToggle?.hostname}. The agent on this PC will be blocked from sending further telemetry.`
        }
        maxWidth="sm"
      >
        <div className="space-y-4 text-xs">
          <div className="flex items-center gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <span>
              {deviceToToggle?.status === 'DISABLED'
                ? 'Device status will transition back to REGISTERED and await heartbeats.'
                : 'Any incoming heartbeat from this machine UID will be rejected with HTTP 403 Forbidden.'}
            </span>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setDisableModalOpen(false);
                setDeviceToToggle(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant={deviceToToggle?.status === 'DISABLED' ? 'primary' : 'danger'}
              size="sm"
              onClick={handleToggleDeviceStatus}
            >
              {deviceToToggle?.status === 'DISABLED' ? 'Enable Device' : 'Disable Device'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Remote Agent Configuration Modal */}
      <Modal
        isOpen={configModalOpen}
        onClose={() => setConfigModalOpen(false)}
        title={targetDeviceId ? 'Configure Workstation Agent' : 'Global Agent Server & Network Settings'}
        description="Update the server IP, port, and timings that the Windows emp_runexe agent connects and sends requests to."
        maxWidth="md"
      >
        <div className="space-y-4 text-xs">
          {pushSuccess && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{pushSuccess}</span>
            </div>
          )}

          <div className="p-3 bg-muted/40 rounded-xl border border-border space-y-3">
            <span className="font-semibold text-foreground text-sm flex items-center gap-2">
              <Server className="w-4 h-4 text-primary" />
              Target Server Routing
            </span>

            <div className="grid grid-cols-3 gap-3">
              <div className="col-span-2">
                <Input
                  label="Server IP / Hostname"
                  value={serverIp}
                  onChange={(e) => setServerIp(e.target.value)}
                  placeholder="192.168.1.253 or domain"
                />
              </div>
              <div>
                <Input
                  label="Server Port"
                  value={serverPort}
                  onChange={(e) => setServerPort(e.target.value)}
                  placeholder="5000"
                  type="number"
                />
              </div>
            </div>

            <div className="p-2 rounded bg-background/80 border border-border text-[11px] font-mono text-muted-foreground">
              Calculated URL: <span className="text-primary font-semibold">http://{serverIp}:{serverPort}</span>
            </div>
          </div>

          <div className="p-3 bg-muted/40 rounded-xl border border-border space-y-3">
            <span className="font-semibold text-foreground text-sm flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-primary" />
              Agent Timing Parameters
            </span>

            <div className="grid grid-cols-2 gap-3">
              <Input
                label="Heartbeat Interval (sec)"
                value={heartbeatSec}
                onChange={(e) => setHeartbeatSec(e.target.value)}
                placeholder="30"
                type="number"
              />
              <Input
                label="Idle Threshold (sec)"
                value={idleSec}
                onChange={(e) => setIdleSec(e.target.value)}
                placeholder="300"
                type="number"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-3 border-t border-border">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handlePushConfig(true)}
              isLoading={isPushing}
              className="w-full sm:w-auto"
            >
              Apply as Global Default
            </Button>

            <Button
              variant="primary"
              size="sm"
              onClick={() => handlePushConfig(false)}
              isLoading={isPushing}
              className="w-full sm:w-auto gap-1.5"
            >
              <Send className="w-3.5 h-3.5" />
              <span>Push Config to Agent</span>
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
