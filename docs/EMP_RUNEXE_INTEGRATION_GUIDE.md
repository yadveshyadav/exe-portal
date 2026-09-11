# `emp_runexe` Windows Service — Web Portal Integration Guide & Contract

> **Target Audience**: AI Agent / Developer implementing or configuring the C#/.NET 8 `emp_runexe` Windows Service agent.
>
> ### 🌐 Active Backend Server URLs:
> - **Another PC on the same Network (Wi-Fi / LAN)**: `http://10.206.47.80:5000` *(Your host machine's active Wi-Fi IP)*
> - **Same PC (Local Testing)**: `http://127.0.0.1:5000` or `http://localhost:5000`
> - **Production**: `https://<your-server-domain-or-public-ip>`

---

## 1. Architectural Rules & Security

1. **Strict Single Destination**: `emp_runexe` must connect **ONLY** to the Flask Backend via HTTP/HTTPS and WebSocket.
   - ❌ **NEVER** connect directly to PostgreSQL.
   - ❌ **NEVER** connect directly to Redis.
   - ❌ **NEVER** connect directly to React.
2. **Device Identity**: Every machine must generate/persist a stable unique hardware identifier GUID (stored as `device_id` / `device_uuid`).
3. **No Dummy Employee Requirement**: Initial registration and heartbeats do **not** require an employee. The portal displays new agents as `Unassigned` until an administrator binds them via the portal UI.
4. **Source IP Detection**: The backend automatically captures the agent's real IP address from network socket headers. The agent does not need to guess its external IP.

---

## 2. Agent Configuration Schema (`appsettings.json`)

Ensure your Windows Service reads configuration from `appsettings.json` (or registry / config file):

```json
{
  "PortalSettings": {
    "ServerUrl": "http://10.206.47.80:5000",
    "CompanyCode": "TEST_CORP",
    "HeartbeatIntervalSeconds": 30,
    "IdleThresholdSeconds": 300,
    "ReconnectIntervalSeconds": 5,
    "RequestTimeoutSeconds": 10
  },
  "AgentSettings": {
    "Version": "1.0.0",
    "ServiceName": "EmpRunExeService"
  }
}
```
*(Note: If running the agent on the same PC where the portal is running, set `"ServerUrl": "http://127.0.0.1:5000"`)*

---

## 3. REST API Contract & Paypoints

### 3.1 Device Registration (`POST /api/v1/agents/register`)
Call this **once on service startup** before starting heartbeat loops.

- **URL**: `POST /api/v1/agents/register`
- **Headers**: `Content-Type: application/json`

#### Request Payload
```json
{
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "hostname": "DESKTOP-FINANCE-01",
  "operating_system": "Windows 11 Enterprise 23H2 (Build 22631.3880)",
  "agent_version": "1.0.0",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "company_code": "TEST_CORP"
}
```

#### Response (HTTP 201 Created or 200 OK)
```json
{
  "success": true,
  "message": "Device registered successfully",
  "device": {
    "id": "e9b21f92-5b9c-4c60-84c4-722a969cf109",
    "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
    "hostname": "DESKTOP-FINANCE-01",
    "status": "REGISTERED"
  }
}
```

#### Error Handling
- **HTTP 403 Forbidden**: The device has been **disabled** by an administrator in the portal. Stop sending events and enter a paused state (retry registration every 5 minutes).
- **HTTP 400 Bad Request**: Missing `device_id` or `hostname`.

---

### 3.2 Periodic Heartbeat (`POST /api/v1/agents/heartbeat`)
Call this **periodically** on a timer (default: every 30 seconds).

- **URL**: `POST /api/v1/agents/heartbeat`
- **Headers**: `Content-Type: application/json`

#### Request Payload
```json
{
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "timestamp": "2026-08-23T13:45:00.000Z",
  "agent_version": "1.0.0",
  "status": "ONLINE",
  "hostname": "DESKTOP-FINANCE-01",
  "operating_system": "Windows 11 Enterprise 23H2",
  "mac_address": "00:1A:2B:3C:4D:5E",
  "company_code": "TEST_CORP",
  "metadata": {
    "cpu_usage_percent": 12.4,
    "memory_usage_mb": 4250,
    "user_idle_seconds": 15,
    "location": {
      "city": "Mumbai",
      "region": "Maharashtra",
      "country": "India",
      "latitude": 19.0760,
      "longitude": 72.8777,
      "timezone": "Asia/Kolkata",
      "isp": "Airtel"
    }
  }
}
```
> **Status values**: `"ONLINE"`, `"ACTIVE"`, `"IDLE"`, `"LOCKED"`.
> **Location**: Automatically saved and mapped in the Portal's Device Management and Live Monitoring views.

#### Response (HTTP 200 OK)
```json
{
  "success": true,
  "data": {
    "device_id": "e9b21f92-5b9c-4c60-84c4-722a969cf109",
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
> **Important**: If the returned `config` contains updated `heartbeat_interval_seconds` or `server_ip`, update the local timer dynamically.

---

### 3.3 Windows Lifecycle Events (`POST /api/v1/agents/events`)
Call this whenever Windows triggers session or power events (Lock, Unlock, Login, Logout, Sleep, Resume).

- **URL**: `POST /api/v1/agents/events`
- **Headers**: `Content-Type: application/json`

#### Request Payload
```json
{
  "device_id": "4B8C1D6E-8F92-4A3B-8C4D-7E8F9A0B1C2D",
  "event_type": "LOCK",
  "company_code": "TEST_CORP",
  "hostname": "DESKTOP-FINANCE-01",
  "metadata": {
    "windows_user": "jane.doe",
    "session_id": 1,
    "event_time": "2026-08-23T13:46:10.000Z"
  }
}
```

#### Allowed `event_type` Values:
- `"LOGIN"`
- `"LOGOUT"`
- `"LOCK"`
- `"UNLOCK"`
- `"SLEEP"`
- `"RESUME"`

---

## 4. C# (.NET 8) Implementation Blueprint

### 4.1 C# Data Transfer Objects (DTOs)

```csharp
using System.Text.Json.Serialization;

namespace EmpRunExe.Core.Models
{
    public class RegisterDeviceRequest
    {
        [JsonPropertyName("device_id")]
        public string DeviceId { get; set; } = string.Empty;

        [JsonPropertyName("hostname")]
        public string Hostname { get; set; } = Environment.MachineName;

        [JsonPropertyName("operating_system")]
        public string OperatingSystem { get; set; } = Environment.OSVersion.ToString();

        [JsonPropertyName("agent_version")]
        public string AgentVersion { get; set; } = "1.0.0";

        [JsonPropertyName("mac_address")]
        public string? MacAddress { get; set; }

        [JsonPropertyName("company_code")]
        public string CompanyCode { get; set; } = "TEST_CORP";
    }

    public class HeartbeatRequest
    {
        [JsonPropertyName("device_id")]
        public string DeviceId { get; set; } = string.Empty;

        [JsonPropertyName("timestamp")]
        public string Timestamp { get; set; } = DateTime.UtcNow.ToString("o");

        [JsonPropertyName("agent_version")]
        public string AgentVersion { get; set; } = "1.0.0";

        [JsonPropertyName("status")]
        public string Status { get; set; } = "ONLINE";

        [JsonPropertyName("hostname")]
        public string Hostname { get; set; } = Environment.MachineName;

        [JsonPropertyName("operating_system")]
        public string OperatingSystem { get; set; } = Environment.OSVersion.ToString();

        [JsonPropertyName("company_code")]
        public string CompanyCode { get; set; } = "TEST_CORP";

        [JsonPropertyName("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public class AgentEventRequest
    {
        [JsonPropertyName("device_id")]
        public string DeviceId { get; set; } = string.Empty;

        [JsonPropertyName("event_type")]
        public string EventType { get; set; } = string.Empty;

        [JsonPropertyName("company_code")]
        public string CompanyCode { get; set; } = "TEST_CORP";

        [JsonPropertyName("hostname")]
        public string Hostname { get; set; } = Environment.MachineName;

        [JsonPropertyName("metadata")]
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public class ApiResponse<T>
    {
        [JsonPropertyName("success")]
        public bool Success { get; set; }

        [JsonPropertyName("data")]
        public T? Data { get; set; }

        [JsonPropertyName("message")]
        public string? Message { get; set; }
    }

    public class HeartbeatResponseData
    {
        [JsonPropertyName("device_uuid")]
        public string DeviceUuid { get; set; } = string.Empty;

        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;

        [JsonPropertyName("config")]
        public RemoteConfig? Config { get; set; }
    }

    public class RemoteConfig
    {
        [JsonPropertyName("server_ip")]
        public string? ServerIp { get; set; }

        [JsonPropertyName("server_port")]
        public int? ServerPort { get; set; }

        [JsonPropertyName("heartbeat_interval_seconds")]
        public int? HeartbeatIntervalSeconds { get; set; }

        [JsonPropertyName("idle_threshold_seconds")]
        public int? IdleThresholdSeconds { get; set; }
    }
}
```

---

### 4.2 C# `ApiClient` Service Implementation

```csharp
using System.Net.Http.Json;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using EmpRunExe.Core.Models;

namespace EmpRunExe.Service.Communication
{
    public interface IApiClient
    {
        Task<bool> RegisterAsync(CancellationToken ct = default);
        Task<HeartbeatResponseData?> SendHeartbeatAsync(string status, Dictionary<string, object>? meta = null, CancellationToken ct = default);
        Task<bool> SendEventAsync(string eventType, Dictionary<string, object>? meta = null, CancellationToken ct = default);
    }

    public class ApiClient : IApiClient
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<ApiClient> _logger;
        private readonly string _deviceId;
        private readonly string _companyCode;
        private readonly string _agentVersion;

        public ApiClient(HttpClient httpClient, ILogger<ApiClient> logger)
        {
            _httpClient = httpClient;
            _logger = logger;
            _deviceId = GetOrGenerateDeviceId();
            _companyCode = "TEST_CORP";
            _agentVersion = "1.0.0";
        }

        public async Task<bool> RegisterAsync(CancellationToken ct = default)
        {
            try
            {
                var payload = new RegisterDeviceRequest
                {
                    DeviceId = _deviceId,
                    Hostname = Environment.MachineName,
                    OperatingSystem = Environment.OSVersion.ToString(),
                    AgentVersion = _agentVersion,
                    CompanyCode = _companyCode
                };

                var response = await _httpClient.PostAsJsonAsync("/api/v1/agents/register", payload, ct);
                if (response.IsSuccessStatusCode)
                {
                    _logger.LogInformation("Agent registered successfully with Portal.");
                    return true;
                }

                if (response.StatusCode == System.Net.HttpStatusCode.Forbidden)
                {
                    _logger.LogWarning("This device is DISABLED by the Portal administrator.");
                    return false;
                }

                _logger.LogWarning("Registration failed with status code: {StatusCode}", response.StatusCode);
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error registering with backend portal.");
                return false;
            }
        }

        public async Task<HeartbeatResponseData?> SendHeartbeatAsync(string status, Dictionary<string, object>? meta = null, CancellationToken ct = default)
        {
            try
            {
                var payload = new HeartbeatRequest
                {
                    DeviceId = _deviceId,
                    Status = status,
                    AgentVersion = _agentVersion,
                    Hostname = Environment.MachineName,
                    OperatingSystem = Environment.OSVersion.ToString(),
                    CompanyCode = _companyCode,
                    Metadata = meta ?? new Dictionary<string, object>()
                };

                var response = await _httpClient.PostAsJsonAsync("/api/v1/agents/heartbeat", payload, ct);
                if (response.IsSuccessStatusCode)
                {
                    var result = await response.Content.ReadFromJsonAsync<ApiResponse<HeartbeatResponseData>>(cancellationToken: ct);
                    return result?.Data;
                }

                if (response.StatusCode == System.Net.HttpStatusCode.Forbidden)
                {
                    _logger.LogWarning("Heartbeat rejected: Device is marked DISABLED.");
                    return null;
                }

                if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                {
                    _logger.LogWarning("Device not found on portal. Re-attempting registration...");
                    await RegisterAsync(ct);
                }

                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Heartbeat delivery failure.");
                return null;
            }
        }

        public async Task<bool> SendEventAsync(string eventType, Dictionary<string, object>? meta = null, CancellationToken ct = default)
        {
            try
            {
                var payload = new AgentEventRequest
                {
                    DeviceId = _deviceId,
                    EventType = eventType.ToUpperInvariant(),
                    CompanyCode = _companyCode,
                    Hostname = Environment.MachineName,
                    Metadata = meta ?? new Dictionary<string, object>()
                };

                var response = await _httpClient.PostAsJsonAsync("/api/v1/agents/events", payload, ct);
                return response.IsSuccessStatusCode;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to send event {EventType}", eventType);
                return false;
            }
        }

        private static string GetOrGenerateDeviceId()
        {
            const string regKey = @"SOFTWARE\EmpRunExe";
            const string valueName = "DeviceId";

            try
            {
                using var key = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(regKey);
                if (key?.GetValue(valueName) is string id && !string.IsNullOrWhiteSpace(id))
                {
                    return id;
                }
            }
            catch { }

            // Generate stable UUID
            var newId = Guid.NewGuid().ToString().ToUpperInvariant();
            try
            {
                using var key = Microsoft.Win32.Registry.LocalMachine.CreateSubKey(regKey);
                key?.SetValue(valueName, newId);
            }
            catch { }

            return newId;
        }
    }
}
```

---

## 5. Lifecycle Execution Flow

```
Windows Service Start
       │
       ▼
1. Read Registry / Settings (Get DeviceId & ServerUrl)
       │
       ▼
2. HTTP POST /api/v1/agents/register
       │
       ├── If 201 Created / 200 OK ──► Proceed to Step 3
       ├── If 403 Forbidden ────────► Pause, retry in 5 min
       └── If Connection Error ─────► Retry in 10s backoff
       │
       ▼
3. Start Heartbeat Background Loop (every 30s)
       │
       ├── HTTP POST /api/v1/agents/heartbeat
       └── Parse remote config (update interval / server IP if modified)
       │
       ▼
4. Listen to Windows Session / Power Events
       │
       ├── On Lock   ──► POST /api/v1/agents/events (event_type: "LOCK")
       ├── On Unlock ──► POST /api/v1/agents/events (event_type: "UNLOCK")
       ├── On Login  ──► POST /api/v1/agents/events (event_type: "LOGIN")
       ├── On Logout ──► POST /api/v1/agents/events (event_type: "LOGOUT")
       └── On Sleep  ──► POST /api/v1/agents/events (event_type: "SLEEP")
```

---

## 6. Testing Verification via PowerShell
 
You can verify communication with the portal immediately from any Windows terminal:
 
```powershell
# Set backend URL ($backendUrl = "http://10.206.47.80:5000" if testing from another PC on LAN, or "http://localhost:5000" if on same PC)
$backendUrl = "http://10.206.47.80:5000"

# 1. Register Device
$regBody = @{
    device_id = "TEST-PC-GUID-001"
    hostname = "PC-WORK-01"
    operating_system = "Windows 11 Pro"
    agent_version = "1.0.0"
    company_code = "TEST_CORP"
} | ConvertTo-Json
 
Invoke-RestMethod -Uri "$backendUrl/api/v1/agents/register" -Method Post -Body $regBody -ContentType "application/json"
 
# 2. Send Heartbeat
$hbBody = @{
    device_id = "TEST-PC-GUID-001"
    agent_version = "1.0.0"
    status = "ONLINE"
    hostname = "PC-WORK-01"
} | ConvertTo-Json
 
Invoke-RestMethod -Uri "$backendUrl/api/v1/agents/heartbeat" -Method Post -Body $hbBody -ContentType "application/json"
```
