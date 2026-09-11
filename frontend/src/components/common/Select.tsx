import { SelectHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { ChevronDown } from 'lucide-react';

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options?: Array<{ label: string; value: string | number }>;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, children, className, id, ...props }, ref) => {
    const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={selectId} className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            {label}
          </label>
        )}
        <div className="relative flex items-center">
          <select
            id={selectId}
            ref={ref}
            className={twMerge(
              clsx(
                'w-full appearance-none bg-card/60 border border-border rounded-lg px-3.5 py-2 pr-9 text-sm text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary cursor-pointer',
                error && 'border-destructive focus:ring-destructive',
                className
              )
            )}
            {...props}
          >
            {options
              ? options.map((opt) => (
                  <option key={opt.value} value={opt.value} className="bg-card text-foreground">
                    {opt.label}
                  </option>
                ))
              : children}
          </select>
          <ChevronDown className="absolute right-3 w-4 h-4 pointer-events-none text-muted-foreground" />
        </div>
        {error && <span className="text-xs font-medium text-destructive">{error}</span>}
      </div>
    );
  }
);

Select.displayName = 'Select';
