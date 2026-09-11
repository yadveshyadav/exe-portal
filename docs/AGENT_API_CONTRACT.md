# emp_runexe Agent API Contract

This document specifies the REST HTTP API contract between the Windows Service agent (`emp_runexe`) and the Flask backend.

---

## 1. Architectural Rules & Security

- **Strict Isolation**: `emp_runexe` connects **ONLY** to the Flask Backend via HTTPS / REST & WSS. It **NEVER** connects directly to PostgreSQL or Redis.
- **Client IP Verification**: The backend ignores any self-reported IP address in the payload body and uses the server-observed network source IP (`request.remote_addr` / `X-Forwarded-For`) to populate `last_ip`.
- **Identity Key**: The canonical device identity is `device_id` (representing the unique machine hardware GUID).

---

## 2. Endpoints

### 2.1 Device Registration

Registers or upserts a Windows workstation in the portal.

- **URL**: `POST /api/v1/agents/register`
- **Authentication**: None / Company enrollment token
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "hostname": "ENG-LAPTOP-042",
  "operating_system": "Windows 11 Enterprise (23H2 22631.3880)",
  "agent_version": "1.0.0",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "company_code": "ACME_CORP"
}
```

#### Response (201 Created / 200 OK)
```json
{
  "success": true,
  "message": "Device registered successfully",
  "device": {
    "id": "dev_9f8e7d6c5b4a",
    "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
    "hostname": "ENG-LAPTOP-042",
    "status": "REGISTERED"
  }
}
```

#### Response (403 Forbidden - When Disabled)
```json
{
  "success": false,
  "message": "Device has been disabled by administrator",
  "errors": ["Device has been disabled by administrator"]
}
```

---

### 2.2 Periodic Heartbeat

Sent by the agent at regular intervals (default: 30 seconds) to maintain live presence and synchronize configuration.

- **URL**: `POST /api/v1/agents/heartbeat`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "timestamp": "2026-08-23T13:45:00Z",
  "agent_version": "1.0.0",
  "status": "ONLINE",
  "hostname": "ENG-LAPTOP-042",
  "operating_system": "Windows 11 Enterprise (23H2)",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "metadata": {
    "cpu_usage_percent": 14.5,
    "memory_usage_mb": 4120
  }
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "data": {
    "device_id": "dev_9f8e7d6c5b4a",
    "device_uuid": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
    "status": "ACK",
    "registered_status": "ONLINE",
    "config": {
      "server_ip": "192.168.1.253",
      "server_port": 5000,
      "heartbeat_interval_seconds": 30,
      "idle_threshold_seconds": 300
    }
  },
  "message": "Heartbeat recorded successfully"
}
```

---

### 2.3 User & System Lifecycle Events

Recorded on Windows lock, unlock, login, logout, sleep, resume.

- **URL**: `POST /api/v1/agents/events`
- **Content-Type**: `application/json`

#### Request Payload
```json
{
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "event_type": "LOCK",
  "company_code": "ACME_CORP",
  "metadata": {
    "username": "jdoe",
    "session_id": 1
  }
}
```

#### Supported Event Types
- `LOGIN`
- `LOGOUT`
- `LOCK`
- `UNLOCK`
- `SLEEP`
- `RESUME`
