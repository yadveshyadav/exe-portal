import { connectionManager, ConnectionStatus } from './connectionManager';

export const realtimeClient = connectionManager;
export { WS_EVENTS } from './events';
export type { ConnectionStatus };
