from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, model_validator

class AgentRegisterRequest(BaseModel):
    device_id: Optional[str] = None
    device_uid: Optional[str] = None
    hostname: str = Field(..., min_length=1)
    operating_system: Optional[str] = "Windows 11"
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    agent_version: Optional[str] = "1.0.0"
    company_code: Optional[str] = None
    company_id: Optional[str] = None
    mac_address: Optional[str] = None

    @model_validator(mode='after')
    def check_device_id(self):
        if not self.device_id and not self.device_uid:
            raise ValueError("device_id or device_uid is required")
        if not self.device_id and self.device_uid:
            self.device_id = self.device_uid
        return self

class AgentHeartbeatRequest(BaseModel):
    device_id: Optional[str] = None
    device_uid: Optional[str] = None
    timestamp: Optional[str] = None
    agent_version: Optional[str] = "1.0.0"
    status: Optional[str] = "ONLINE"
    hostname: Optional[str] = None
    company_code: Optional[str] = None
    company_id: Optional[str] = None
    mac_address: Optional[str] = None
    os_version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode='after')
    def check_device_id(self):
        if not self.device_id and not self.device_uid:
            raise ValueError("device_id or device_uid is required")
        if not self.device_id and self.device_uid:
            self.device_id = self.device_uid
        return self

class AgentConfigPushRequest(BaseModel):
    server_url: Optional[str] = None
    server_ip: Optional[str] = None
    server_port: Optional[int] = Field(None, ge=1, le=65535)
    policy_id: Optional[str] = None
    heartbeat_interval: Optional[int] = Field(None, ge=5, le=600)
    heartbeat_interval_seconds: Optional[int] = Field(None, ge=5, le=600)
    idle_threshold: Optional[int] = Field(None, ge=30, le=3600)
    idle_threshold_seconds: Optional[int] = Field(None, ge=30, le=3600)
    reconnect_interval: Optional[int] = Field(None, ge=5, le=300)
    reconnect_interval_seconds: Optional[int] = Field(None, ge=5, le=300)
    event_batch_size: Optional[int] = Field(None, ge=1, le=100)
