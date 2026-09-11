import React from 'react';
import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import { PermissionGate } from './PermissionGate';

export interface SidebarItemProps {
  label: string;
  to: string;
  icon?: React.ReactNode;
  permission?: string;
  badge?: string | number;
  exact?: boolean;
}

export const SidebarItem: React.FC<SidebarItemProps> = ({
  label,
  to,
  icon,
  permission,
  badge,
}) => {
  const content = (
    <NavLink
      to={to}
      className={({ isActive }) =>
        clsx(
          'flex items-center justify-between px-3 py-2 text-xs font-medium rounded-lg transition-colors group select-none',
          isActive
            ? 'bg-primary/15 text-primary font-semibold border-l-2 border-primary'
            : 'text-muted-foreground hover:bg-muted hover:text-foreground'
        )
      }
    >
      <div className="flex items-center gap-2.5">
        {icon && <span className="w-4 h-4 shrink-0">{icon}</span>}
        <span className="truncate">{label}</span>
      </div>
      {badge !== undefined && (
        <span className="px-1.5 py-0.2 text-[10px] rounded-full bg-muted text-muted-foreground group-hover:bg-card">
          {badge}
        </span>
      )}
    </NavLink>
  );

  if (permission) {
    return <PermissionGate permission={permission}>{content}</PermissionGate>;
  }

  return content;
};
