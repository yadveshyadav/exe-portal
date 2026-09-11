import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export interface ActivityPoint {
  time: string;
  active: number;
  idle: number;
}

export const WorkforceActivityChart: React.FC<{ data?: ActivityPoint[] }> = ({ data }) => {
  // Default zero baseline across working hours if no telemetry recorded yet
  const hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'];
  const chartData = data && data.length > 0 ? data : hours.map((t) => ({ time: t, active: 0, idle: 0 }));

  return (
    <div className="p-5 rounded-xl bg-card border border-border shadow-sm flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-foreground">Hourly Workforce Activity</h3>
          <p className="text-xs text-muted-foreground">Aggregated active vs idle endpoints today</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-primary" />
            <span className="text-muted-foreground">Active</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm bg-amber-500" />
            <span className="text-muted-foreground">Idle</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="activeGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="idleGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="time" stroke="#6b7280" fontSize={11} tickLine={false} />
            <YAxis stroke="#6b7280" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                borderColor: 'hsl(var(--border))',
                borderRadius: '0.5rem',
                fontSize: '12px',
              }}
            />
            <Area
              type="monotone"
              dataKey="active"
              stroke="#3b82f6"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#activeGrad)"
            />
            <Area
              type="monotone"
              dataKey="idle"
              stroke="#f59e0b"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#idleGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
