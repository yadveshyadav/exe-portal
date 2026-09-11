# Security & Zero-Trust Device Architecture

## 1. Authentication & Session Security
- **JWT (JSON Web Tokens)**: Short-lived access tokens (60 minutes) combined with long-lived refresh tokens (30 days).
- **Password Hashing**: Bcrypt with salted rounds.
- **Authorization Enforcement**: Dual-enforced. UI elements use `<PermissionGate>` for visibility, but all REST controllers strictly execute server-side `@require_permission` checks before querying or mutating the database.

---

## 2. Windows Agent Zero-Trust Enrollment
1. **Device Identification**: Windows agents report a unique hardware hash (`device_uid`).
2. **Registration Protocol**: During initial bootstrap, the agent authenticates with the company enrollment token.
3. **Safe Command Restrictions**: Only pre-approved diagnostic and telemetry sync commands (`HEALTH_CHECK`, `REFRESH_CONFIGURATION`, `SYNC`, `CHECK_VERSION`) are allowed. Arbitrary command execution is strictly disallowed.

---

## 3. Immutable Auditing
All modifications to employee records, department structures, policy configurations, device assignments, and user privileges are written to the `audit_logs` table with previous and updated JSON snapshots.
