from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_employees: int
    total_devices: int
    online_devices: int
    offline_devices: int
    active_devices: int
    idle_devices: int
    locked_devices: int
    active_alerts: int
