import React from 'react';
import { SidebarItem } from '../navigation/SidebarItem';
import {
  LayoutDashboard,
  Users,
  Laptop,
  CalendarCheck,
  Timer,
  History,
  ShieldCheck,
} from 'lucide-react';

export const Sidebar: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
  onClose,
}) => {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-40 h-screen w-64 border-r border-border bg-card flex flex-col transition-transform duration-200 lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex items-center gap-3 px-5 h-16 border-b border-border">
          <div className="p-2 rounded-lg bg-primary/10 border border-primary/20 text-primary">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-foreground leading-none">
              EMP PORTAL
            </h1>
            <span className="text-[10px] font-mono text-muted-foreground tracking-wider uppercase">
              Workforce & Activity
            </span>
          </div>
        </div>

        {/* Streamlined Navigation Menu */}
        <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          {/* Main Dashboard */}
          <div>
            <SidebarItem
              label="Dashboard"
              to="/dashboard"
              icon={<LayoutDashboard className="w-4 h-4" />}
            />
          </div>

          {/* WORKFORCE & DEVICES */}
          <div className="space-y-1">
            <span className="px-3 text-[10px] font-bold text-muted-foreground/70 uppercase tracking-wider font-mono">
              Management
            </span>
            <SidebarItem
              label="Employees"
              to="/workforce/employees"
              icon={<Users className="w-4 h-4" />}
            />
            <SidebarItem
              label="Enrolled Devices"
              to="/devices/all"
              icon={<Laptop className="w-4 h-4" />}
            />
          </div>

          {/* TIME & SESSION ACTIVITY */}
          <div className="space-y-1">
            <span className="px-3 text-[10px] font-bold text-muted-foreground/70 uppercase tracking-wider font-mono">
              Activity & Sessions
            </span>
            <SidebarItem
              label="Attendance & Duration"
              to="/workforce/attendance"
              icon={<CalendarCheck className="w-4 h-4" />}
            />
            <SidebarItem
              label="Active Work Sessions"
              to="/monitoring/sessions"
              icon={<Timer className="w-4 h-4" />}
            />
            <SidebarItem
              label="Login / Logout / Sleep Events"
              to="/monitoring/events"
              icon={<History className="w-4 h-4" />}
            />
          </div>
        </div>

        {/* Footer info */}
        <div className="p-3 border-t border-border bg-card/60 flex items-center justify-between text-[11px] text-muted-foreground">
          <span className="font-mono">emp_runexe agent</span>
          <span className="flex items-center gap-1.5 font-medium text-emerald-500">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" /> Live Hub
          </span>
        </div>
      </aside>
    </>
  );
};
