import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { realtimeClient } from '@/websocket/client';
import { WS_EVENTS } from '@/websocket/events';
import { ConnectionStatus } from '@/websocket/connectionManager';
import { DeviceStatusChangedPayload, WebSocketEventMessage } from '@/types/websocket';

interface RealtimeContextType {
  lastDeviceUpdate: DeviceStatusChangedPayload | null;
  lastEvent: any | null;
  lastAlert: any | null;
  connectionStatus: ConnectionStatus;
  isConnected: boolean;
}

const RealtimeContext = createContext<RealtimeContextType | undefined>(undefined);

export const RealtimeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const queryClient = useQueryClient();
  const [lastDeviceUpdate, setLastDeviceUpdate] = useState<DeviceStatusChangedPayload | null>(null);
  const [lastEvent, setLastEvent] = useState<any | null>(null);
  const [lastAlert, setLastAlert] = useState<any | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(realtimeClient.getStatus());

  useEffect(() => {
    const unsubStatus = realtimeClient.onStatusChange((status) => {
      setConnectionStatus(status);
    });

    const handleDeviceEvent = (msg: WebSocketEventMessage<any>) => {
      if (msg?.data || msg?.payload) {
        const payloadData = msg.data || msg.payload;
        setLastDeviceUpdate(payloadData);
        // Seamless cache refresh
        queryClient.invalidateQueries({ queryKey: ['devices'] });
        queryClient.invalidateQueries({ queryKey: ['device'] });
        queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        queryClient.invalidateQueries({ queryKey: ['events'] });
      }
    };

    const unsubDeviceStatus = realtimeClient.on(WS_EVENTS.DEVICE_STATUS_CHANGED, handleDeviceEvent);
    const unsubDeviceReg = realtimeClient.on(WS_EVENTS.DEVICE_REGISTERED, handleDeviceEvent);
    const unsubDeviceOnline = realtimeClient.on(WS_EVENTS.DEVICE_ONLINE, handleDeviceEvent);
    const unsubDeviceOffline = realtimeClient.on(WS_EVENTS.DEVICE_OFFLINE, handleDeviceEvent);
    const unsubDeviceStale = realtimeClient.on(WS_EVENTS.DEVICE_STALE, handleDeviceEvent);
    const unsubHeartbeat = realtimeClient.on(WS_EVENTS.HEARTBEAT_RECEIVED, handleDeviceEvent);
    const unsubAgentVer = realtimeClient.on(WS_EVENTS.AGENT_VERSION_CHANGED, handleDeviceEvent);

    const unsubEvent = realtimeClient.on(WS_EVENTS.EVENT_RECORDED, (msg: WebSocketEventMessage) => {
      if (msg?.data) {
        setLastEvent(msg.data);
        queryClient.invalidateQueries({ queryKey: ['events'] });
        queryClient.invalidateQueries({ queryKey: ['dashboard'] });
        queryClient.invalidateQueries({ queryKey: ['devices'] });
      }
    });

    const unsubAlert = realtimeClient.on(WS_EVENTS.ALERT_TRIGGERED, (msg: WebSocketEventMessage) => {
      if (msg?.data) {
        setLastAlert(msg.data);
        queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      }
    });

    return () => {
      unsubStatus();
      unsubDeviceStatus();
      unsubDeviceReg();
      unsubDeviceOnline();
      unsubDeviceOffline();
      unsubDeviceStale();
      unsubHeartbeat();
      unsubAgentVer();
      unsubEvent();
      unsubAlert();
    };
  }, [queryClient]);

  return (
    <RealtimeContext.Provider
      value={{
        lastDeviceUpdate,
        lastEvent,
        lastAlert,
        connectionStatus,
        isConnected: connectionStatus === 'CONNECTED',
      }}
    >
      {children}
    </RealtimeContext.Provider>
  );
};

export const useRealtime = () => {
  const context = useContext(RealtimeContext);
  if (!context) {
    throw new Error('useRealtime must be used within a RealtimeProvider');
  }
  return context;
};
