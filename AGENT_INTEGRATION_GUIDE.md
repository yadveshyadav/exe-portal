# Windows Agent (`emp_runexe`) Integration Specification

This document is the exact integration contract for the **`emp_runexe`** Windows Agent to connect with the **Employee Control Portal**.

---

## 1. Scope & Privacy Boundaries

For this phase, the Windows Agent **only** tracks:
1. **Login & Logout Timestamps** (User Windows session logon, logoff, workstation lock/unlock).
2. **Sleep & Resume Modes** (Machine entering sleep/suspend vs waking up/resuming).
3. **Active / Idle Work Session Duration** (30-second heartbeats tracking whether the machine is actively being used).

> [!IMPORTANT]
> **No invasive monitoring is permitted** (No keylogging, no screen captures, no browser history scraping, and no arbitrary shell execution).

---

## 2. Portal Server Connection Details

| Parameter | Value |
| :--- | :--- |
| **Backend Base URL** | `http://localhost:5000` *(or your server IP: `http://<SERVER_IP>:5000`)* |
| **Company Code** | `ACME` |
| **Company ID** | `21219b0d-19d1-43c7-a7cd-52a6df0b25a4` |
| **REST Heartbeat URL** | `POST http://localhost:5000/api/v1/agents/heartbeat` |
| **REST Events URL** | `POST http://localhost:5000/api/v1/agents/events` |
| **WebSocket URL** | `ws://localhost:5000/socket.io/?EIO=4&transport=websocket` |

---

## 3. REST API Contracts

### 3.1 Periodic Heartbeat (`POST /api/v1/agents/heartbeat`)
The agent sends this **every 30 seconds** while running.

#### Headers:
`Content-Type: application/json`

#### Request Body:
```json
{
  "company_code": "ACME",
  "device_uid": "WIN-UUID-YOUR-MACHINE-HASH",
  "hostname": "WORKSTATION-01",
  "status": "ACTIVE",
  "agent_version": "1.0.0",
  "ip_address": "192.168.1.105",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "os_version": "Windows 11 Enterprise (23H2)"
}
```

* **Valid `status` values**: `"ACTIVE"`, `"IDLE"`, `"LOCKED"`, `"OFFLINE"`

#### Success Response (`200 OK` with Remote Configuration):
```json
{
  "success": true,
  "data": {
    "device_id": "3733c667-a1f8-4194-b34e-63771fa5b538",
    "status": "ACK",
    "registered_status": "ACTIVE",
    "config": {
      "server_url": "http://192.168.1.253:5000",
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

### 3.2 Lifecycle Events (`POST /api/v1/agents/events`)
The agent sends this immediately when a state transition occurs (Login, Logout, Sleep, Resume, Lock, Unlock).

#### Headers:
`Content-Type: application/json`

#### Request Body:
```json
{
  "company_code": "ACME",
  "device_uid": "WIN-UUID-YOUR-MACHINE-HASH",
  "hostname": "WORKSTATION-01",
  "event_type": "LOGIN",
  "metadata": {
    "windows_user": "JohnDoe",
    "domain": "CORP"
  }
}
```

#### Supported `event_type` Values:
- `"LOGIN"` - Windows user logged on / work day started.
- `"LOGOUT"` - Windows user logged off / workstation shutting down.
- `"SLEEP"` - Computer entered sleep / suspend / standby mode.
- `"RESUME"` - Computer woke up from sleep / resume.
- `"LOCK"` - Workstation locked (`Win + L` or screen lock).
- `"UNLOCK"` - Workstation unlocked by user.

---

## 4. Complete C# Integration Service with Remote Config (`TelemetryService.cs`)

You can directly drop this service class into your C# `emp_runexe` project:

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Win32;

namespace EmpRunExe.Services
{
    public class TelemetryService
    {
        private readonly HttpClient _httpClient;
        private string _serverBaseUrl = "http://192.168.1.253:5000";
        private string _companyCode = "ACME";
        private readonly string _deviceUid;
        private Timer? _heartbeatTimer;
        private int _heartbeatIntervalMs = 30000;

        public TelemetryService()
        {
            _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(10) };
            _deviceUid = GetOrCreateMachineGuid();

            // Hook Windows System Events (Power & Session)
            SystemEvents.PowerModeChanged += OnPowerModeChanged;
            SystemEvents.SessionSwitch += OnSessionSwitch;
            SystemEvents.SessionEnded += OnSessionEnded;
        }

        public void Start()
        {
            // Report initial Logon event
            _ = SendEventAsync("LOGIN", new { user = Environment.UserName });

            // Schedule periodic heartbeat
            _heartbeatTimer = new Timer(async _ => await SendHeartbeatAsync("ACTIVE"), null, 0, _heartbeatIntervalMs);
        }

        public void Stop()
        {
            _heartbeatTimer?.Dispose();
            _ = SendEventAsync("LOGOUT", new { reason = "Service Stopped" });
        }

        /// <summary>
        /// Sends periodic heartbeat with active/idle state and processes dynamic server config updates.
        /// </summary>
        public async Task SendHeartbeatAsync(string status = "ACTIVE")
        {
            try
            {
                var payload = new
                {
                    company_code = _companyCode,
                    device_uid = _deviceUid,
                    hostname = Environment.MachineName,
                    status = status,
                    agent_version = "1.0.0",
                    os_version = Environment.OSVersion.VersionString
                };

                var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");
                var response = await _httpClient.PostAsync($"{_serverBaseUrl}/api/v1/agents/heartbeat", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseJson = await response.Content.ReadAsStringAsync();
                    using var doc = JsonDocument.Parse(responseJson);
                    
                    // Check if server returned updated config (e.g. new Server IP / Port / URL)
                    if (doc.RootElement.TryGetProperty("data", out var dataElem) &&
                        dataElem.TryGetProperty("config", out var configElem))
                    {
                        ApplyServerConfiguration(configElem);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Heartbeat Error] {ex.Message}");
            }
        }

        /// <summary>
        /// Dynamically updates the destination server URL, IP, port, and timings sent from the web portal.
        /// </summary>
        public void ApplyServerConfiguration(JsonElement config)
        {
            if (config.TryGetProperty("server_url", out var serverUrlProp))
            {
                var newUrl = serverUrlProp.GetString();
                if (!string.IsNullOrEmpty(newUrl) && newUrl != _serverBaseUrl)
                {
                    Console.WriteLine($"[Agent Config Update] Switching Server URL from {_serverBaseUrl} -> {newUrl}");
                    _serverBaseUrl = newUrl;
                }
            }

            if (config.TryGetProperty("heartbeat_interval_seconds", out var intervalProp) &&
                intervalProp.TryGetInt32(out var intervalSec) && intervalSec >= 5)
            {
                var newIntervalMs = intervalSec * 1000;
                if (newIntervalMs != _heartbeatIntervalMs)
                {
                    _heartbeatIntervalMs = newIntervalMs;
                    _heartbeatTimer?.Change(0, _heartbeatIntervalMs);
                    Console.WriteLine($"[Agent Config Update] Heartbeat interval adjusted to {intervalSec}s");
                }
            }
        }

        /// <summary>
        /// Sends immediate lifecycle events (LOGIN, LOGOUT, SLEEP, RESUME, LOCK, UNLOCK).
        /// </summary>
        public async Task SendEventAsync(string eventType, object? metadata = null)
        {
            try
            {
                var payload = new
                {
                    company_code = _companyCode,
                    device_uid = _deviceUid,
                    hostname = Environment.MachineName,
                    event_type = eventType,
                    metadata = metadata ?? new { }
                };

                var content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json");
                await _httpClient.PostAsync($"{_serverBaseUrl}/api/v1/agents/events", content);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Event Error] {ex.Message}");
            }
        }

        // --- Windows Event Handlers ---

        private void OnPowerModeChanged(object sender, PowerModeChangedEventArgs e)
        {
            if (e.Mode == PowerModes.Suspend)
            {
                // Machine going to Sleep / Standby
                _ = SendEventAsync("SLEEP", new { reason = "System Suspend" });
            }
            else if (e.Mode == PowerModes.Resume)
            {
                // Machine Waking up
                _ = SendEventAsync("RESUME", new { reason = "System Resume" });
            }
        }

        private void OnSessionSwitch(object sender, SessionSwitchEventArgs e)
        {
            switch (e.Reason)
            {
                case SessionSwitchReason.SessionLock:
                    _ = SendEventAsync("LOCK");
                    break;
                case SessionSwitchReason.SessionUnlock:
                    _ = SendEventAsync("UNLOCK");
                    break;
                case SessionSwitchReason.SessionLogon:
                    _ = SendEventAsync("LOGIN");
                    break;
                case SessionSwitchReason.SessionLogoff:
                    _ = SendEventAsync("LOGOUT");
                    break;
            }
        }

        private void OnSessionEnded(object sender, SessionEndedEventArgs e)
        {
            _ = SendEventAsync("LOGOUT", new { reason = e.Reason.ToString() });
        }

        private string GetOrCreateMachineGuid()
        {
            try
            {
                using var key = RegistryKey.OpenBaseKey(RegistryHive.LocalMachine, RegistryView.Registry64)
                                           .OpenSubKey(@"SOFTWARE\Microsoft\Cryptography");
                return key?.GetValue("MachineGuid")?.ToString() ?? Guid.NewGuid().ToString();
            }
            catch
            {
                return Environment.MachineName + "-DEFAULT-UID";
            }
        }
    }
}
```

---

## 5. How the Portal Displays These Records

1. **Dashboard**: Shows online/offline status, active/idle count, and today's total work time.
2. **Live Monitoring**: Displays active status and live session durations updating in real-time.
3. **Attendance View (`/workforce/attendance`)**: Automatically computes `First Check-in` (on first `LOGIN`), `Last Check-out` (on `LOGOUT` or last seen heartbeat), and total active work hours.
4. **Work Sessions View (`/monitoring/sessions`)**: Granular daily active vs idle duration bars.
5. **Event History (`/monitoring/events`)**: Complete audit trail showing exact timestamps of every `LOGIN`, `LOGOUT`, `SLEEP`, `RESUME`, `LOCK`, and `UNLOCK` event.
