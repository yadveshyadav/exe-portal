# WebSocket Protocol Specification

## 1. Connection Lifecycle

### 1.1 Windows Agent Connection
- **Endpoint**: `ws://<server>/socket.io/?EIO=4&transport=websocket`
- **Authentication**: Sent during handshake / `AGENT_HEARTBEAT` payload with `company_id` and `device_uid`.

```json
// Event: "AGENT_HEARTBEAT"
{
  "device_uid": "WIN-UID-001-9842",
  "company_id": "c1f72b64-...",
  "hostname": "WS-001-RIVERS",
  "status": "ACTIVE",
  "agent_version": "1.2.4",
  "ip_address": "192.168.1.101",
  "mac_address": "00:1A:2B:3C:4D:01",
  "metadata": {
    "cpu_usage_pct": 12.4,
    "ram_usage_pct": 45.1
  }
}
```

- **Server Response**: Event `AGENT_HEARTBEAT_ACK`
```json
{
  "device_id": "d8204a91-...",
  "status": "ACK",
  "server_time": "2026-08-22T02:30:00Z"
}
```

---

### 1.2 Web Portal Frontend Connection
- **Subscription**: On connect, portal client emits `PORTAL_SUBSCRIBE`:
```json
{
  "company_id": "c1f72b64-...",
  "user_id": "u439810-..."
}
```

- **Server Broadcasts Received by Portal**:
  - `DEVICE_STATUS_CHANGED`
  - `ALERT_TRIGGERED`
  - `ALERT_RESOLVED`
  - `COMMAND_STATUS_UPDATED`
  - `CONFIGURATION_UPDATED`
