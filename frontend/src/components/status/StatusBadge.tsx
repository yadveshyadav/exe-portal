import React from 'react';
import { DeviceStatus } from '@/types/device';
import { clsx } from 'clsx';

export interface StatusBadgeProps {
  status: DeviceStatus | string;
  size?: 'sm' | 'md';
  showPulse?: boolean;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showPulse = true,
  className = '',
}) => {
  const normStatus = (status || 'UNKNOWN').toUpperCase();

  const configs: Record<
    string,
    { label: string; bg: string; text: string; dot: string; pulse: boolean }
  > = {
    REGISTERED: {
      label: 'Registered',
      bg: 'bg-sky-500/10 border-sky-500/20',
      text: 'text-sky-400',
      dot: 'bg-sky-400',
      pulse: true,
    },
    ONLINE: {
      label: 'Online',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
      pulse: true,
    },
    ACTIVE: {
      label: 'Active',
      bg: 'bg-blue-500/10 border-blue-500/20',
      text: 'text-blue-400',
      dot: 'bg-blue-500',
      pulse: true,
    },
    IDLE: {
      label: 'Idle',
      bg: 'bg-amber-500/10 border-amber-500/20',
      text: 'text-amber-400',
      dot: 'bg-amber-500',
      pulse: false,
    },
    STALE: {
      label: 'Stale',
      bg: 'bg-amber-500/15 border-amber-500/30',
      text: 'text-amber-300',
      dot: 'bg-amber-400',
      pulse: false,
    },
    LOCKED: {
      label: 'Locked',
      bg: 'bg-purple-500/10 border-purple-500/20',
      text: 'text-purple-400',
      dot: 'bg-purple-500',
      pulse: false,
    },
    OFFLINE: {
      label: 'Offline',
      bg: 'bg-zinc-500/10 border-zinc-500/20',
      text: 'text-zinc-400',
      dot: 'bg-zinc-500',
      pulse: false,
    },
    DISABLED: {
      label: 'Disabled',
      bg: 'bg-rose-950/20 border-rose-900/30',
      text: 'text-rose-400/80',
      dot: 'bg-rose-500',
      pulse: false,
    },
    ERROR: {
      label: 'Agent Error',
      bg: 'bg-rose-500/15 border-rose-500/30',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
      pulse: true,
    },
    LOGIN: {
      label: 'Login',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
      pulse: true,
    },
    LOGOUT: {
      label: 'Logout',
      bg: 'bg-rose-500/10 border-rose-500/20',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
      pulse: false,
    },
    SLEEP: {
      label: 'Sleep',
      bg: 'bg-indigo-500/10 border-indigo-500/20',
      text: 'text-indigo-400',
      dot: 'bg-indigo-500',
      pulse: false,
    },
    RESUME: {
      label: 'Resume',
      bg: 'bg-cyan-500/10 border-cyan-500/20',
      text: 'text-cyan-400',
      dot: 'bg-cyan-500',
      pulse: true,
    },
    LOCK: {
      label: 'Locked',
      bg: 'bg-purple-500/10 border-purple-500/20',
      text: 'text-purple-400',
      dot: 'bg-purple-500',
      pulse: false,
    },
    UNLOCK: {
      label: 'Unlocked',
      bg: 'bg-emerald-500/10 border-emerald-500/20',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
      pulse: true,
    },
    UNKNOWN: {
      label: 'Registered',
      bg: 'bg-zinc-500/10 border-zinc-500/20',
      text: 'text-zinc-400',
      dot: 'bg-zinc-400',
      pulse: false,
    },
  };

  const config = configs[normStatus] || configs.UNKNOWN;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[11px] gap-1.5',
    md: 'px-2.5 py-1 text-xs gap-2',
  };

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-md border tracking-wide uppercase font-mono select-none',
        config.bg,
        config.text,
        sizeClasses[size],
        className
      )}
      aria-label={`Status: ${config.label}`}
    >
      <span className="relative flex h-2 w-2">
        {showPulse && config.pulse && (
          <span
            className={clsx(
              'animate-ping absolute inline-flex h-full w-full rounded-full opacity-75',
              config.dot
            )}
          />
        )}
        <span className={clsx('relative inline-flex rounded-full h-2 w-2', config.dot)} />
      </span>
      <span>{config.label}</span>
    </span>
  );
};
