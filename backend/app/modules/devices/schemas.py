from typing import Optional
from pydantic import BaseModel, Field

class DeviceUpdateRequest(BaseModel):
    hostname: Optional[str] = None
    employee_id: Optional[str] = None
    status: Optional[str] = None

class DeviceAssignEmployeeRequest(BaseModel):
    employee_id: Optional[str] = None

class DeviceEnrollmentTokenRequest(BaseModel):
    hostname: str = Field(...)
    device_uid: str = Field(...)

class DeviceHeartbeatPayload(BaseModel):
    device_uid: str
    hostname: str
    agent_version: str = "1.0.0"
    status: str = "ACTIVE"
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    os_version: Optional[str] = None
    metadata: Optional[dict] = None
