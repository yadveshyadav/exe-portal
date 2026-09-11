import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { employeesApi, departmentsApi } from '@/api/employees';
import { devicesApi } from '@/api/devices';
import { Employee } from '@/types/workforce';
import { DataTable, Column } from '@/components/tables/DataTable';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Select } from '@/components/common/Select';
import { Badge } from '@/components/common/Badge';
import { Modal } from '@/components/modals/Modal';
import { ConfirmationDialog } from '@/components/modals/ConfirmationDialog';
import { usePermissions } from '@/hooks/usePermissions';
import { PERMISSIONS } from '@/constants/permissions';
import { Plus, Search, Edit2, UserX, Laptop, Building2, Mail, Phone } from 'lucide-react';
import { useForm } from 'react-hook-form';

export const EmployeesPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { can } = usePermissions();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('');

  // Modals state
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [deactivateDialogOpen, setDeactivateDialogOpen] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);

  // Queries
  const { data, isLoading } = useQuery({
    queryKey: ['employees', page, search, deptFilter],
    queryFn: () =>
      employeesApi.list({
        page,
        page_size: 15,
        search: search || undefined,
        department_id: deptFilter || undefined,
      }),
  });

  const { data: deptData } = useQuery({
    queryKey: ['departments'],
    queryFn: departmentsApi.list,
  });

  const { data: unassignedDevices } = useQuery({
    queryKey: ['devices', 'unassigned'],
    queryFn: () => devicesApi.list({ unassigned: true }),
    enabled: assignModalOpen,
  });

  // Forms
  const createForm = useForm<Partial<Employee>>();
  const editForm = useForm<Partial<Employee>>();
  const [selectedDeviceId, setSelectedDeviceId] = useState('');

  // Mutations
  const createMutation = useMutation({
    mutationFn: employeesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setCreateModalOpen(false);
      createForm.reset();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Employee> }) =>
      employeesApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setEditModalOpen(false);
    },
  });

  const deactivateMutation = useMutation({
    mutationFn: employeesApi.deactivate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setDeactivateDialogOpen(false);
    },
  });

  const assignDeviceMutation = useMutation({
    mutationFn: ({ empId, devId }: { empId: string; devId: string }) =>
      employeesApi.assignDevice(empId, devId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['employees'] });
      setAssignModalOpen(false);
    },
  });

  const handleEdit = (emp: Employee) => {
    setSelectedEmployee(emp);
    editForm.reset(emp);
    setEditModalOpen(true);
  };

  const handleAssign = (emp: Employee) => {
    setSelectedEmployee(emp);
    setSelectedDeviceId('');
    setAssignModalOpen(true);
  };

  const handleDeactivate = (emp: Employee) => {
    setSelectedEmployee(emp);
    setDeactivateDialogOpen(true);
  };

  const columns: Column<Employee>[] = [
    {
      header: 'Employee',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold text-xs">
            {row.first_name[0]}
            {row.last_name[0]}
          </div>
          <div>
            <span className="font-semibold text-foreground text-sm block">{row.full_name}</span>
            <span className="text-xs text-muted-foreground font-mono">{row.employee_code}</span>
          </div>
        </div>
      ),
    },
    {
      header: 'Department',
      accessor: (row) => (
        <span className="text-xs text-muted-foreground flex items-center gap-1.5">
          <Building2 className="w-3.5 h-3.5" />
          {row.department_name || 'None'}
        </span>
      ),
    },
    {
      header: 'Designation',
      accessor: (row) => <span className="text-xs text-foreground">{row.designation || 'Staff'}</span>,
    },
    {
      header: 'Email',
      accessor: (row) => (
        <span className="text-xs text-muted-foreground font-mono flex items-center gap-1.5">
          <Mail className="w-3 h-3" />
          {row.email}
        </span>
      ),
    },
    {
      header: 'Status',
      accessor: (row) => (
        <Badge variant={row.status === 'ACTIVE' ? 'success' : 'default'} size="sm">
          {row.status}
        </Badge>
      ),
    },
    {
      header: 'Actions',
      className: 'text-right',
      accessor: (row) => (
        <div className="flex items-center justify-end gap-1.5">
          {can(PERMISSIONS.EMPLOYEES_EDIT) && (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  handleAssign(row);
                }}
                title="Assign Device"
              >
                <Laptop className="w-4 h-4 text-primary" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  handleEdit(row);
                }}
                title="Edit Employee"
              >
                <Edit2 className="w-4 h-4 text-muted-foreground" />
              </Button>
            </>
          )}
          {can(PERMISSIONS.EMPLOYEES_DEACTIVATE) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                handleDeactivate(row);
              }}
              title="Deactivate Employee"
            >
              <UserX className="w-4 h-4 text-destructive" />
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Inline Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Employees</h1>
          <p className="text-xs text-muted-foreground">
            Manage corporate workforce profiles, designations, and endpoint hardware assignments.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Input
            placeholder="Search employees..."
            leftIcon={<Search className="w-4 h-4" />}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-52 text-xs h-9"
          />

          <Select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            options={[
              { label: 'All Departments', value: '' },
              ...(deptData?.items || []).map((d) => ({ label: d.name, value: d.id })),
            ]}
            className="w-40 text-xs h-9"
          />

          {can(PERMISSIONS.EMPLOYEES_CREATE) && (
            <Button onClick={() => setCreateModalOpen(true)} className="h-9 px-3 gap-1.5">
              <Plus className="w-4 h-4" /> Add Employee
            </Button>
          )}
        </div>
      </div>

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={data?.items || []}
        isLoading={isLoading}
        page={data?.pagination?.page}
        totalPages={data?.pagination?.total_pages}
        onPageChange={setPage}
        keyExtractor={(row) => row.id}
      />

      {/* Create Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Add New Employee"
        description="Register a new employee profile in the workforce directory."
      >
        <form
          onSubmit={createForm.handleSubmit((vals) => createMutation.mutate(vals))}
          className="space-y-4"
        >
          <div className="grid grid-cols-2 gap-3">
            <Input label="First Name" required {...createForm.register('first_name', { required: true })} />
            <Input label="Last Name" required {...createForm.register('last_name', { required: true })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Employee Code" placeholder="e.g. EMP-009" required {...createForm.register('employee_code', { required: true })} />
            <Input label="Email Address" type="email" required {...createForm.register('email', { required: true })} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Designation" placeholder="e.g. Software Engineer" {...createForm.register('designation')} />
            <Select
              label="Department"
              {...createForm.register('department_id')}
              options={[
                { label: 'Select Department', value: '' },
                ...(deptData?.items || []).map((d) => ({ label: d.name, value: d.id })),
              ]}
            />
          </div>
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" type="button" onClick={() => setCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={createMutation.isPending}>
              Create Profile
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Edit Employee"
        description="Update profile and departmental assignment details."
      >
        <form
          onSubmit={editForm.handleSubmit((vals) =>
            selectedEmployee && updateMutation.mutate({ id: selectedEmployee.id, data: vals })
          )}
          className="space-y-4"
        >
          <div className="grid grid-cols-2 gap-3">
            <Input label="First Name" required {...editForm.register('first_name')} />
            <Input label="Last Name" required {...editForm.register('last_name')} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Designation" {...editForm.register('designation')} />
            <Input label="Phone" {...editForm.register('phone')} />
          </div>
          <Select
            label="Department"
            {...editForm.register('department_id')}
            options={[
              { label: 'Select Department', value: '' },
              ...(deptData?.items || []).map((d) => ({ label: d.name, value: d.id })),
            ]}
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" type="button" onClick={() => setEditModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={updateMutation.isPending}>
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

      {/* Assign Device Modal */}
      <Modal
        isOpen={assignModalOpen}
        onClose={() => setAssignModalOpen(false)}
        title={`Assign Device to ${selectedEmployee?.full_name}`}
        description="Bind an enrolled Windows workstation endpoint to this employee."
      >
        <div className="space-y-4">
          <Select
            label="Available Devices"
            value={selectedDeviceId}
            onChange={(e) => setSelectedDeviceId(e.target.value)}
            options={[
              { label: 'Select an enrolled device...', value: '' },
              ...(unassignedDevices?.items || []).map((d) => ({
                label: `${d.hostname} (${d.device_uid}) - ${d.os_name}`,
                value: d.id,
              })),
            ]}
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setAssignModalOpen(false)}>
              Cancel
            </Button>
            <Button
              disabled={!selectedDeviceId}
              isLoading={assignDeviceMutation.isPending}
              onClick={() =>
                selectedEmployee &&
                assignDeviceMutation.mutate({
                  empId: selectedEmployee.id,
                  devId: selectedDeviceId,
                })
              }
            >
              Confirm Assignment
            </Button>
          </div>
        </div>
      </Modal>

      {/* Deactivate Confirmation */}
      <ConfirmationDialog
        isOpen={deactivateDialogOpen}
        onClose={() => setDeactivateDialogOpen(false)}
        onConfirm={() => selectedEmployee && deactivateMutation.mutate(selectedEmployee.id)}
        title="Deactivate Employee"
        message={`Are you sure you want to deactivate ${selectedEmployee?.full_name}? Their devices will be unassigned and portal access revoked. Historical records remain preserved.`}
        confirmLabel="Deactivate"
        isLoading={deactivateMutation.isPending}
      />
    </div>
  );
};
