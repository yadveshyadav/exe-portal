# System Architecture Specification

## 1. High-Level Architecture Overview

The **Employee Control Portal** is an enterprise management platform designed to orchestrate and monitor enrolled `emp_runexe` Windows Agents deployed across corporate workstations.

```text
┌─────────────────────────────────────────────────────────────┐
│                    React + TypeScript UI                    │
│      (Vite, Tailwind, TanStack Query, Recharts, WSS)        │
└──────────────┬───────────────────────────────▲──────────────┘
               │ HTTPS (REST API)              │ WSS (Live Updates)
               ▼                               │
┌─────────────────────────────────────────────────────────────┐
│                   Flask Backend Application                 │
│  - JWT Auth / RBAC Middleware  - Blueprints / Modules       │
│  - Validation (Pydantic)       - Service Layer              │
│  - Audit Logging Middleware    - WebSocket Event Handler    │
└──────┬───────────────────────┬────────────────────────▲─────┘
       │                       │                        │
       │ SQLAlchemy ORM        │ Redis Pub/Sub          │ Agent WSS / REST
       ▼                       ▼                        │
┌──────────────┐       ┌────────────────┐      ┌────────┴─────┐
│  PostgreSQL  │       │  Redis Cache & │      │  emp_runexe  │
│ (exe_portal) │       │    Pub/Sub     │◄─────┤   Windows    │
│  (History,   │       │  (Live State,  │      │    Agent     │
│  Relational, │       │  Heartbeats)   │      └──────────────┘
│   Audit)     │       │                │
└──────────────┘       └────────────────┘
```

---

## 2. Core Architectural Pillars

### 2.1 State Segregation: Redis vs PostgreSQL
- **Live / In-Flight State (Redis)**: High-frequency agent heartbeats (every 30s) are recorded in Redis keys (`device:state:{device_id}`) with automatic TTL expiration.
- **Durable Historical Data (PostgreSQL `exe_portal`)**: Relational profiles (Companies, Departments, Employees, Roles, Permissions), aggregated WorkSessions, daily Attendance records, and immutable Audit/Event logs.

### 2.2 Dual-Channel WebSocket Architecture
1. **Agent Telemetry Channel**: The C# Windows Service (`emp_runexe`) transmits lightweight heartbeats, presence state (`ACTIVE`, `IDLE`, `LOCKED`), and execution results.
2. **Admin Portal Broadcasting**: The Python backend broadcasts delta updates (`DEVICE_STATUS_CHANGED`, `ALERT_TRIGGERED`) over Redis Pub/Sub directly to connected React clients in room `company:{company_id}`.

### 2.3 Layered Frontend Architecture
- **API Client**: Axios instance with automated Bearer token injection and seamless refresh token rotation.
- **Server State**: Managed via TanStack Query with optimistic in-place WebSocket updates.
- **RBAC Visibility**: UI navigation and action buttons guarded via declarative `<PermissionGate>` wrappers.
- **Zero-Flicker Grid**: Live Monitoring table updates row properties in-place without page reloading.
