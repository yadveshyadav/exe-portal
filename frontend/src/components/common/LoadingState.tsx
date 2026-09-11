import React from 'react';
import { Loader2, AlertCircle, FolderOpen } from 'lucide-react';
import { Button } from './Button';

export const LoadingState: React.FC<{ message?: string; className?: string }> = ({
  message = 'Loading data...',
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center ${className}`}>
      <Loader2 className="w-8 h-8 text-primary animate-spin mb-3" />
      <p className="text-sm font-medium text-muted-foreground">{message}</p>
    </div>
  );
};

export const ErrorState: React.FC<{
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}> = ({
  title = 'Something went wrong',
  message = 'An unexpected error occurred while fetching data.',
  onRetry,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center bg-destructive/5 rounded-xl border border-destructive/20 ${className}`}>
      <div className="p-3 bg-destructive/10 rounded-full text-destructive mb-3">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h3 className="text-base font-semibold text-foreground mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-md mb-4">{message}</p>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
};

export const EmptyState: React.FC<{
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
  className?: string;
}> = ({
  title = 'No records found',
  description = 'There are no items matching the current filter criteria.',
  actionLabel,
  onAction,
  icon,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center p-12 text-center bg-card/40 rounded-xl border border-dashed border-border ${className}`}>
      <div className="p-3 bg-muted rounded-full text-muted-foreground mb-3">
        {icon || <FolderOpen className="w-6 h-6" />}
      </div>
      <h3 className="text-base font-semibold text-foreground mb-1">{title}</h3>
      <p className="text-sm text-muted-foreground max-w-md mb-4">{description}</p>
      {actionLabel && onAction && (
        <Button variant="primary" size="sm" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};
