import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { departmentsApi } from '@/api/employees';
import { Department } from '@/types/workforce';
import { DataTable, Column } from '@/components/tables/DataTable';
import { Button } from '@/components/common/Button';
import { Input } from '@/components/common/Input';
import { Modal } from '@/components/modals/Modal';
import { ConfirmationDialog } from '@/components/modals/ConfirmationDialog';
import { usePermissions } from '@/hooks/usePermissions';
import { PERMISSIONS } from '@/constants/permissions';
import { Plus, Building2, Edit2, Trash2 } from 'lucide-react';
import { useForm } from 'react-hook-form';

export const DepartmentsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { can } = usePermissions();
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedDept, setSelectedDept] = useState<Department | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['departments'],
    queryFn: departmentsApi.list,
  });

  const createForm = useForm<Partial<Department>>();
  const editForm = useForm<Partial<Department>>();

  const createMutation = useMutation({
    mutationFn: departmentsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setCreateModalOpen(false);
      createForm.reset();
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Department> }) =>
      departmentsApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setEditModalOpen(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: departmentsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['departments'] });
      setDeleteDialogOpen(false);
    },
  });

  const handleEdit = (dept: Department) => {
    setSelectedDept(dept);
    editForm.reset(dept);
    setEditModalOpen(true);
  };

  const handleDelete = (dept: Department) => {
    setSelectedDept(dept);
    setDeleteDialogOpen(true);
  };

  const columns: Column<Department>[] = [
    {
      header: 'Department Name',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <Building2 className="w-4 h-4" />
          </div>
          <div>
            <span className="font-semibold text-foreground text-sm block">{row.name}</span>
            <span className="text-xs text-muted-foreground font-mono">{row.code}</span>
          </div>
        </div>
      ),
    },
    {
      header: 'Description',
      accessor: (row) => (
        <span className="text-xs text-muted-foreground">{row.description || 'No description provided.'}</span>
      ),
    },
    {
      header: 'Created At',
      accessor: (row) => (
        <span className="text-xs text-muted-foreground font-mono">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      header: 'Actions',
      className: 'text-right',
      accessor: (row) => (
        <div className="flex items-center justify-end gap-1.5">
          {can(PERMISSIONS.DEPARTMENTS_MANAGE) && (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleEdit(row)}
                title="Edit Department"
              >
                <Edit2 className="w-4 h-4 text-muted-foreground" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDelete(row)}
                title="Delete Department"
              >
                <Trash2 className="w-4 h-4 text-destructive" />
              </Button>
            </>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Departments</h1>
          <p className="text-xs text-muted-foreground">
            Structure and organize organizational units, business functions, and teams.
          </p>
        </div>

        {can(PERMISSIONS.DEPARTMENTS_MANAGE) && (
          <Button onClick={() => setCreateModalOpen(true)}>
            <Plus className="w-4 h-4 mr-1.5" /> Add Department
          </Button>
        )}
      </div>

      <DataTable
        columns={columns}
        data={data?.items || []}
        isLoading={isLoading}
        keyExtractor={(row) => row.id}
      />

      {/* Create Modal */}
      <Modal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        title="Add Department"
        description="Create a new organizational business unit."
      >
        <form
          onSubmit={createForm.handleSubmit((vals) => createMutation.mutate(vals))}
          className="space-y-4"
        >
          <Input label="Department Name" required {...createForm.register('name', { required: true })} />
          <Input label="Department Code" placeholder="e.g. ENG or SALES" required {...createForm.register('code', { required: true })} />
          <Input label="Description" placeholder="Optional description..." {...createForm.register('description')} />
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" type="button" onClick={() => setCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" isLoading={createMutation.isPending}>
              Create Department
            </Button>
          </div>
        </form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={editModalOpen}
        onClose={() => setEditModalOpen(false)}
        title="Edit Department"
        description="Modify department details."
      >
        <form
          onSubmit={editForm.handleSubmit((vals) =>
            selectedDept && updateMutation.mutate({ id: selectedDept.id, data: vals })
          )}
          className="space-y-4"
        >
          <Input label="Department Name" required {...editForm.register('name')} />
          <Input label="Description" {...editForm.register('description')} />
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

      {/* Delete Confirmation */}
      <ConfirmationDialog
        isOpen={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        onConfirm={() => selectedDept && deleteMutation.mutate(selectedDept.id)}
        title="Delete Department"
        message={`Are you sure you want to remove ${selectedDept?.name}? Employees in this department will remain but will become unassigned.`}
        confirmLabel="Delete"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
};
