import React from 'react';
import { Users, Activity, Clock, ShieldAlert } from 'lucide-react';

export interface LiveWorkforceBreakdown {
  active: number;
  idle: number;
  offline: number;
  locked: number;
}

export const LiveWorkforceCard: React.FC<{
  breakdown: LiveWorkforceBreakdown;
  totalDevices: number;
}> = ({ breakdown, totalDevices }) => {
  const total = totalDevices || 1;
  const activePct = Math.round((breakdown.active / total) * 100);
  const idlePct = Math.round((breakdown.idle / total) * 100);
  const lockedPct = Math.round((breakdown.locked / total) * 100);
  const offlinePct = Math.max(0, 100 - activePct - idlePct - lockedPct);

  return (
    <div className="p-5 rounded-xl bg-card border border-border shadow-sm flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-base font-semibold text-foreground">Live Workforce Status</h3>
          <span className="text-xs text-muted-foreground">Real-time Telemetry</span>
        </div>
        <p className="text-xs text-muted-foreground mb-4">
          Current distribution of enrolled desktop endpoints and active user sessions.
        </p>

        {/* Stacked Progress Bar */}
        <div className="w-full h-3 bg-muted rounded-full overflow-hidden flex mb-6">
          <div
            style={{ width: `${activePct}%` }}
            className="bg-blue-500 transition-all duration-500"
            title={`Active: ${breakdown.active} (${activePct}%)`}
          />
          <div
            style={{ width: `${idlePct}%` }}
            className="bg-amber-500 transition-all duration-500"
            title={`Idle: ${breakdown.idle} (${idlePct}%)`}
          />
          <div
            style={{ width: `${lockedPct}%` }}
            className="bg-purple-500 transition-all duration-500"
            title={`Locked: ${breakdown.locked} (${lockedPct}%)`}
          />
          <div
            style={{ width: `${offlinePct}%` }}
            className="bg-zinc-600 transition-all duration-500"
            title={`Offline: ${breakdown.offline} (${offlinePct}%)`}
          />
        </div>

        {/* Status Legend Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-blue-500/5 rounded-lg border border-blue-500/15">
            <div className="flex items-center gap-1.5 text-blue-400 text-xs font-semibold uppercase">
              <Activity className="w-3.5 h-3.5" />
              <span>Active</span>
            </div>
            <span className="text-xl font-bold text-foreground mt-1 block">
              {breakdown.active}
            </span>
            <span className="text-[11px] text-muted-foreground">{activePct}% total</span>
          </div>

          <div className="p-3 bg-amber-500/5 rounded-lg border border-amber-500/15">
            <div className="flex items-center gap-1.5 text-amber-400 text-xs font-semibold uppercase">
              <Clock className="w-3.5 h-3.5" />
              <span>Idle</span>
            </div>
            <span className="text-xl font-bold text-foreground mt-1 block">
              {breakdown.idle}
            </span>
            <span className="text-[11px] text-muted-foreground">{idlePct}% total</span>
          </div>

          <div className="p-3 bg-purple-500/5 rounded-lg border border-purple-500/15">
            <div className="flex items-center gap-1.5 text-purple-400 text-xs font-semibold uppercase">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Locked</span>
            </div>
            <span className="text-xl font-bold text-foreground mt-1 block">
              {breakdown.locked}
            </span>
            <span className="text-[11px] text-muted-foreground">{lockedPct}% total</span>
          </div>

          <div className="p-3 bg-zinc-500/5 rounded-lg border border-zinc-500/15">
            <div className="flex items-center gap-1.5 text-zinc-400 text-xs font-semibold uppercase">
              <Users className="w-3.5 h-3.5" />
              <span>Offline</span>
            </div>
            <span className="text-xl font-bold text-foreground mt-1 block">
              {breakdown.offline}
            </span>
            <span className="text-[11px] text-muted-foreground">{offlinePct}% total</span>
          </div>
        </div>
      </div>
    </div>
  );
};
