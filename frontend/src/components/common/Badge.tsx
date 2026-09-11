import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'outline';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'md',
  className,
}) => {
  const base = 'inline-flex items-center font-medium rounded-full';

  const variants = {
    default: 'bg-muted text-muted-foreground',
    primary: 'bg-primary/15 text-primary border border-primary/20',
    success: 'bg-emerald-500/15 text-emerald-500 border border-emerald-500/20',
    warning: 'bg-amber-500/15 text-amber-500 border border-amber-500/20',
    danger: 'bg-rose-500/15 text-rose-500 border border-rose-500/20',
    outline: 'border border-border text-foreground',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-0.5 text-xs',
  };

  return (
    <span className={twMerge(clsx(base, variants[variant], sizes[size], className))}>
      {children}
    </span>
  );
};
