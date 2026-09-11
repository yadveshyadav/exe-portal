import React from 'react';
import { clsx } from 'clsx';

export interface MetricCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  color?: 'blue' | 'emerald' | 'amber' | 'purple' | 'rose' | 'zinc';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  color = 'blue',
  className = '',
}) => {
  const colorMap = {
    blue: 'text-blue-500 bg-blue-500/10 border-blue-500/20',
    emerald: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
    purple: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
    rose: 'text-rose-500 bg-rose-500/10 border-rose-500/20',
    zinc: 'text-zinc-400 bg-zinc-500/10 border-zinc-500/20',
  };

  return (
    <div
      className={clsx(
        'p-5 rounded-xl bg-card border border-border flex flex-col justify-between shadow-sm hover:border-primary/30 transition-all',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          {title}
        </span>
        <div className={clsx('p-2.5 rounded-lg border', colorMap[color])}>
          {icon}
        </div>
      </div>

      <div className="mt-4 flex items-baseline justify-between">
        <span className="text-2xl font-bold tracking-tight text-foreground">{value}</span>
        {trend && (
          <span
            className={clsx(
              'text-xs font-medium px-2 py-0.5 rounded-full',
              trend.isPositive ? 'bg-emerald-500/15 text-emerald-400' : 'bg-rose-500/15 text-rose-400'
            )}
          >
            {trend.value}
          </span>
        )}
      </div>

      {subtitle && <p className="text-xs text-muted-foreground mt-1.5">{subtitle}</p>}
    </div>
  );
};
