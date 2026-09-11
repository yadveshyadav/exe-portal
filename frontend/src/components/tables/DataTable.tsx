import React from 'react';
import { ChevronLeft, ChevronRight, ArrowUpDown } from 'lucide-react';
import { LoadingState, EmptyState } from '../common/LoadingState';
import { Button } from '../common/Button';

export interface Column<T> {
  header: string;
  accessor?: keyof T | ((row: T) => React.ReactNode);
  className?: string;
  sortable?: boolean;
}

export interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  page?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  onRowClick?: (row: T) => void;
  keyExtractor: (row: T) => string;
}

export function DataTable<T>({
  columns,
  data,
  isLoading = false,
  emptyTitle = 'No data available',
  emptyDescription = 'No records match your criteria.',
  page,
  totalPages,
  onPageChange,
  onRowClick,
  keyExtractor,
}: DataTableProps<T>) {
  if (isLoading) {
    return <LoadingState message="Fetching data..." className="min-h-[280px]" />;
  }

  if (!data || data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} className="my-4" />;
  }

  return (
    <div className="w-full flex flex-col bg-card rounded-xl border border-border overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-foreground">
          <thead className="bg-muted/50 border-b border-border text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            <tr>
              {columns.map((col, idx) => (
                <th key={idx} className={`px-5 py-3.5 ${col.className || ''}`}>
                  <div className="flex items-center gap-1.5">
                    <span>{col.header}</span>
                    {col.sortable && <ArrowUpDown className="w-3.5 h-3.5 text-muted-foreground/60" />}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.map((row) => {
              const rowKey = keyExtractor(row);
              return (
                <tr
                  key={rowKey}
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`hover:bg-muted/40 transition-colors ${
                    onRowClick ? 'cursor-pointer' : ''
                  }`}
                >
                  {columns.map((col, cIdx) => {
                    let cellContent: React.ReactNode = null;
                    if (typeof col.accessor === 'function') {
                      cellContent = col.accessor(row);
                    } else if (col.accessor) {
                      cellContent = (row[col.accessor] as any)?.toString();
                    }
                    return (
                      <td key={cIdx} className={`px-5 py-3.5 ${col.className || ''}`}>
                        {cellContent}
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      {page !== undefined && totalPages !== undefined && totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between px-5 py-3.5 border-t border-border bg-card/60">
          <span className="text-xs text-muted-foreground">
            Page <span className="font-semibold text-foreground">{page}</span> of{' '}
            <span className="font-semibold text-foreground">{totalPages}</span>
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
            >
              <ChevronLeft className="w-4 h-4 mr-1" /> Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
            >
              Next <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
