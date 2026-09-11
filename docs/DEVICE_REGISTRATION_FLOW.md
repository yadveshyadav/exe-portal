# End-to-End Device Registration & Live Management Flow

This document details the complete lifecycle of a Windows workstation running the `emp_runexe` service connecting to the Web Portal.

```mermaid
sequenceDiagram
    autonumber
    participant Agent as emp_runexe (Windows Service)
    participant Flask as Flask Backend (API & WS)
    participant Redis as Redis (Fast Live State)
    participant PG as PostgreSQL (Persistence)
    participant React as React Admin Portal

    Note over Agent,React: 1. Initial Device Registration
    Agent->>Flask: POST /api/v1/agents/register (device_id, hostname, os, agent_version)
    Flask->>PG: Upsert Device record (status='REGISTERED', employee_id=NULL)
    Flask->>Redis: SET device:{device_uuid}:presence (status='REGISTERED', ttl=120s)
    Flask->>React: Broadcast WS event: DEVICE_REGISTERED
    React-->>React: Live update table (appears immediately without page reload)
    Flask-->>Agent: HTTP 201 Created (device registered)

    Note over Agent,React: 2. Periodic Live Heartbeat
    Agent->>Flask: POST /api/v1/agents/heartbeat (device_id, agent_version, status='ONLINE')
    Flask->>PG: UPDATE Device (last_seen_at=now, status='ONLINE', last_ip=observed_ip)
    Flask->>Redis: SET device:{device_uuid}:presence (status='ONLINE', ttl=120s)
    Flask->>React: Broadcast WS event: DEVICE_ONLINE
    React-->>React: Live Status Badge turns Green (ONLINE)
    Flask-->>Agent: HTTP 200 OK (ACK + updated agent config)

    Note over Agent,React: 3. Employee Assignment
    Admin->>React: Click 'Assign' on workstation row -> Select 'Jane Doe'
    React->>Flask: POST /api/v1/devices/{id}/assign { employee_id: "emp_123" }
    Flask->>PG: UPDATE Device (employee_id='emp_123')
    Flask->>Redis: Update presence cache employee_id
    Flask->>PG: Write AuditLog (DEVICE_ASSIGNED)
    Flask-->>React: HTTP 200 OK

    Note over Agent,React: 4. Administrative Device Disable / Enable
    Admin->>React: Click 'Disable Device'
    React->>Flask: POST /api/v1/devices/{id}/disable
    Flask->>PG: UPDATE Device (status='DISABLED')
    Flask->>Redis: SET device status='DISABLED'
    Flask-->>React: HTTP 200 OK
    Agent->>Flask: Next Heartbeat (device_id)
    Flask-->>Agent: HTTP 403 Forbidden (Device disabled)
```

---

## Key Lifecycle States

1. **`REGISTERED`**:
   - Workstation has called `POST /api/v1/agents/register`.
   - Employee is `Unassigned` (`employee_id = NULL`).
   - Device appears immediately in portal device inventory.
2. **`ONLINE`**:
   - Periodic heartbeat (`POST /api/v1/agents/heartbeat`) received within the last 60 seconds.
   - Redis key is active (`device:{device_uuid}:presence`).
3. **`STALE`**:
   - No heartbeat received for >60 seconds.
4. **`OFFLINE`**:
   - No heartbeat received for >120 seconds.
   - Watchdog updates status to `OFFLINE` and notifies connected React admins.
5. **`DISABLED`**:
   - An administrator disabled the workstation.
   - All subsequent agent requests receive HTTP 403 Forbidden.
