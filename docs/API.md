# REST API Specification (`/api/v1/*`)

All responses follow the standardized JSON envelope:
```json
{
  "success": true,
  "data": {},
  "message": "Operation description",
  "errors": []
}
```

---

## 1. Authentication (`/api/v1/auth`)

### `POST /api/v1/auth/login`
- **Request Body**: `{ "username_or_email": "admin", "password": "..." }`
- **Response**: `{ "access_token": "...", "refresh_token": "...", "user": { ... } }`

### `POST /api/v1/auth/refresh`
- **Request Body**: `{ "refresh_token": "..." }`
- **Response**: `{ "access_token": "..." }`

### `GET /api/v1/auth/me` (Auth: Bearer JWT)
- **Response**: Full user profile, permissions, and company context.

---

## 2. Dashboard (`/api/v1/dashboard`)

### `GET /api/v1/dashboard/summary`
- **Permission**: `dashboard.view`
- **Response**: Total employee count, online/offline devices, active/idle distribution, and alert counts.

### `GET /api/v1/dashboard/recent-events`
- **Permission**: `dashboard.view`
- **Response**: Most recent telemetry event stream.

---

## 3. Workforce Management (`/api/v1/employees`, `/api/v1/departments`)

- `GET /api/v1/employees`: Filtered and paginated employee profiles.
- `POST /api/v1/employees`: Create new employee.
- `PUT /api/v1/employees/{id}`: Update employee metadata.
- `DELETE /api/v1/employees/{id}`: Soft-delete (deactivate) employee.
- `POST /api/v1/employees/{id}/assign-device`: Bind workstation to employee.
- `GET /api/v1/departments`: Department hierarchy list.

---

## 4. Device & Monitoring (`/api/v1/devices`, `/api/v1/monitoring`)

- `GET /api/v1/devices`: List enrolled workstations with status filters.
- `GET /api/v1/devices/{id}`: Deep telemetry, agent version, recent events, and sessions.
- `GET /api/v1/monitoring/live`: High-frequency live grid feed.
- `GET /api/v1/attendance`: Daily employee check-in and total work time.
- `GET /api/v1/sessions`: Active vs idle session duration records.

---

## 5. Control, Policies & Alerts (`/api/v1/policies`, `/api/v1/alerts`, `/api/v1/commands`)

- `GET /api/v1/policies`: List policies.
- `POST /api/v1/policies`: Create agent policy.
- `GET /api/v1/alerts`: Paginated system alerts.
- `POST /api/v1/alerts/{id}/resolve`: Resolve alert with operator notes.
- `POST /api/v1/commands/dispatch`: Dispatch safe administrative command (`HEALTH_CHECK`, `REFRESH_CONFIGURATION`, `SYNC`, `CHECK_VERSION`).
