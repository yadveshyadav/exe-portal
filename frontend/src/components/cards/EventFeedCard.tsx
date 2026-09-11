import React from 'react';
import { TelemetryEvent } from '@/types/monitoring';
import { StatusBadge } from '../status/StatusBadge';
import { Radio, AlertCircle, Laptop } from 'lucide-react';

export const EventFeedCard: React.FC<{ events: TelemetryEvent[] }> = ({ events }) => {
  return (
    <div className="p-5 rounded-xl bg-card border border-border shadow-sm flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-primary animate-pulse" />
          <h3 className="text-base font-semibold text-foreground">Recent Telemetry Events</h3>
        </div>
        <span className="text-xs text-muted-foreground font-mono">Live Stream</span>
      </div>

      {events.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-8 text-muted-foreground text-xs text-center">
          <AlertCircle className="w-6 h-6 mb-2 text-muted-foreground/60" />
          No recent events recorded yet.
        </div>
      ) : (
        <div className="space-y-3 overflow-y-auto max-h-[340px] pr-1">
          {events.map((event) => (
            <div
              key={event.id}
              className="p-3 bg-muted/40 hover:bg-muted/70 rounded-lg border border-border/60 transition-colors flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 bg-card rounded-md border border-border text-muted-foreground">
                  <Laptop className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-foreground">
                      {event.hostname || 'Device'}
                    </span>
                    <span className="text-[11px] text-muted-foreground">
                      • {event.employee_name || 'Unassigned'}
                    </span>
                  </div>
                  <span className="text-[11px] text-muted-foreground font-mono">
                    {new Date(event.received_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              <StatusBadge status={event.event_type} size="sm" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
