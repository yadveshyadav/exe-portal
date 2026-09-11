import { io, Socket } from 'socket.io-client';
import { WS_EVENTS } from './events';
import { WebSocketEventMessage } from '@/types/websocket';

export type ConnectionStatus = 'DISCONNECTED' | 'CONNECTING' | 'CONNECTED' | 'RECONNECTING' | 'ERROR';

export class ConnectionManager {
  private socket: Socket | null = null;
  private status: ConnectionStatus = 'DISCONNECTED';
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private statusListeners: Set<(status: ConnectionStatus) => void> = new Set();
  private currentCompanyId: string | null = null;
  private currentUserId: string | null = null;

  public connect(companyId?: string, userId?: string) {
    if (companyId) this.currentCompanyId = companyId;
    if (userId) this.currentUserId = userId;

    if (this.socket?.connected) {
      if (this.currentCompanyId) {
        this.subscribeToCompany(this.currentCompanyId, this.currentUserId || undefined);
      }
      return;
    }

    this.setStatus('CONNECTING');
    const url = window.location.origin;

    this.socket = io(url, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: Infinity,
      timeout: 10000,
    });

    this.socket.on('connect', () => {
      this.setStatus('CONNECTED');
      if (this.currentCompanyId) {
        this.subscribeToCompany(this.currentCompanyId, this.currentUserId || undefined);
      }
    });

    this.socket.on('disconnect', (reason) => {
      console.warn('[WebSocket] Disconnected:', reason);
      this.setStatus('DISCONNECTED');
    });

    this.socket.on('connect_error', (error) => {
      console.warn('[WebSocket] Connection Error:', error.message);
      this.setStatus('ERROR');
    });

    this.socket.on('reconnect_attempt', () => {
      this.setStatus('RECONNECTING');
    });

    // Wire all declared event constants
    Object.values(WS_EVENTS).forEach((eventName) => {
      this.socket?.on(eventName, (payload: WebSocketEventMessage) => {
        this.dispatch(eventName, payload);
      });
    });
  }

  public subscribeToCompany(companyId: string, userId?: string) {
    this.currentCompanyId = companyId;
    if (userId) this.currentUserId = userId;

    if (this.socket?.connected) {
      this.socket.emit(WS_EVENTS.PORTAL_SUBSCRIBE, {
        company_id: companyId,
        user_id: userId,
      });
    }
  }

  public on(event: string, callback: (data: any) => void) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)?.add(callback);

    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  public onStatusChange(callback: (status: ConnectionStatus) => void) {
    this.statusListeners.add(callback);
    callback(this.status);
    return () => {
      this.statusListeners.delete(callback);
    };
  }

  public getStatus(): ConnectionStatus {
    return this.status;
  }

  public isConnected(): boolean {
    return this.status === 'CONNECTED';
  }

  private setStatus(status: ConnectionStatus) {
    this.status = status;
    this.statusListeners.forEach((cb) => cb(status));
  }

  private dispatch(event: string, data: any) {
    const callbacks = this.listeners.get(event);
    if (callbacks) {
      callbacks.forEach((cb) => {
        try {
          cb(data);
        } catch (e) {
          console.error(`[WebSocket] Error in handler for event ${event}:`, e);
        }
      });
    }
  }

  public disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.setStatus('DISCONNECTED');
    }
  }
}

export const connectionManager = new ConnectionManager();
