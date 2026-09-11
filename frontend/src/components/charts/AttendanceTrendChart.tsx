import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

export const AttendanceTrendChart: React.FC<{ data?: Array<{ date: string; present: number; half_day: number }> }> = ({
  data,
}) => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const chartData = data && data.length > 0 ? data : days.map((d) => ({ date: d, present: 0, half_day: 0 }));

  return (
    <div className="p-5 rounded-xl bg-card border border-border shadow-sm flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-foreground">7-Day Attendance Trend</h3>
          <p className="text-xs text-muted-foreground">Present vs partial workforce check-ins</p>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis dataKey="date" stroke="#6b7280" fontSize={11} tickLine={false} />
            <YAxis stroke="#6b7280" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'hsl(var(--card))',
                borderColor: 'hsl(var(--border))',
                borderRadius: '0.5rem',
                fontSize: '12px',
              }}
            />
            <Bar dataKey="present" fill="#10b981" radius={[4, 4, 0, 0]} name="Present" />
            <Bar dataKey="half_day" fill="#f59e0b" radius={[4, 4, 0, 0]} name="Half Day" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
