import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { Menu, LogOut, Shield, Sun, Moon } from 'lucide-react';
import { Button } from '../common/Button';

export const Header: React.FC<{ onMenuClick: () => void }> = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const [isDark, setIsDark] = useState<boolean>(() => {
    return document.documentElement.classList.contains('dark');
  });

  const toggleTheme = () => {
    const nextDark = !isDark;
    setIsDark(nextDark);
    if (nextDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  };

  useEffect(() => {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark') {
      document.documentElement.classList.add('dark');
      setIsDark(true);
    } else if (saved === 'light') {
      document.documentElement.classList.remove('dark');
      setIsDark(false);
    }
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 border-b border-border bg-card px-5 flex items-center justify-between shadow-sm">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted focus:outline-none"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Live system state tag */}
        <div className="hidden sm:flex items-center gap-2 px-2.5 py-1 rounded-md bg-muted/80 text-xs border border-border">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-medium text-foreground">Operational</span>
          <span className="text-muted-foreground">• Server Latency 12ms</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Theme Toggle Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleTheme}
          className="text-muted-foreground hover:text-foreground"
          title={isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme'}
        >
          {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-700" />}
        </Button>

        {/* User Identity & Logout */}
        <div className="flex items-center gap-3 pl-3 border-l border-border">
          <div className="flex flex-col items-end">
            <span className="text-xs font-semibold text-foreground">
              {user?.full_name || user?.username}
            </span>
            <div className="flex items-center gap-1 text-[11px] text-muted-foreground font-mono">
              <Shield className="w-3 h-3 text-primary" />
              <span>{user?.roles?.[0] || 'Administrator'}</span>
            </div>
          </div>

          <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold text-xs uppercase">
            {user?.username?.[0] || 'A'}
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={logout}
            className="text-muted-foreground hover:text-destructive hover:bg-destructive/10"
            title="Sign out"
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  );
};
