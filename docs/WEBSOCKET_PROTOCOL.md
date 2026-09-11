# WebSocket Protocol Specification (Phase 2A)

This document defines the Socket.IO real-time event protocol between the Flask Backend and React Admin Portal.

---

## 1. Rooms and Subscriptions

When an authenticated admin loads the React portal, the client subscribes to its company room:

### Client -> Server: `PORTAL_SUBSCRIBE`
```json
{
  "company_id": "comp_12345",
  "user_id": "usr_67890"
}
```

The server joins the client socket to `company_{company_id}`.

---

## 2. Real-Time Events (Server -> Portal Client)

### 2.1 `DEVICE_REGISTERED`
Emitted immediately when a new Windows PC runs `emp_runexe` and posts registration.

```json
{
  "type": "DEVICE_REGISTERED",
  "company_id": "comp_12345",
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "hostname": "ENG-LAPTOP-042",
  "payload": {
    "id": "dev_9f8e7d6c5b4a",
    "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
    "hostname": "ENG-LAPTOP-042",
    "status": "REGISTERED",
    "operating_system": "Windows 11 Enterprise (23H2)",
    "agent_version": "1.0.0",
    "employee_id": null,
    "employee_name": "Unassigned"
  },
  "timestamp": "2026-08-23T13:45:00Z"
}
```

---

### 2.2 `DEVICE_ONLINE`
Emitted when an agent sends its periodic heartbeat or reconnects.

```json
{
  "type": "DEVICE_ONLINE",
  "company_id": "comp_12345",
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "hostname": "ENG-LAPTOP-042",
  "timestamp": "2026-08-23T13:45:30Z"
}
```

---

### 2.3 `DEVICE_OFFLINE`
Emitted by the watchdog timer or disconnect handler when a device misses heartbeats.

```json
{
  "type": "DEVICE_OFFLINE",
  "company_id": "comp_12345",
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "hostname": "ENG-LAPTOP-042",
  "timestamp": "2026-08-23T13:47:30Z"
}
```

---

### 2.4 `DEVICE_STALE`
Emitted when a device has not sent a heartbeat in >60 seconds.

```json
{
  "type": "DEVICE_STALE",
  "company_id": "comp_12345",
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "timestamp": "2026-08-23T13:46:30Z"
}
```

---

### 2.5 `AGENT_VERSION_CHANGED`
Emitted when an existing endpoint reports an upgraded `agent_version`.

```json
{
  "type": "AGENT_VERSION_CHANGED",
  "company_id": "comp_12345",
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "hostname": "ENG-LAPTOP-042",
  "old_version": "1.0.0",
  "new_version": "2.0.0",
  "timestamp": "2026-08-23T13:48:00Z"
}
```

---

### 2.6 `CONFIGURATION_UPDATED`
Emitted when an administrator pushes updated server IP/port or intervals.

```json
{
  "type": "CONFIGURATION_UPDATED",
  "company_id": "comp_12345",
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "config": {
    "server_ip": "192.168.1.253",
    "server_port": 5000,
    "heartbeat_interval_seconds": 30,
    "idle_threshold_seconds": 300
  }
}
```
