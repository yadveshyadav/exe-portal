from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class EmployeeCreateRequest(BaseModel):
    employee_code: str = Field(..., min_length=2, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    phone: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[str] = None
    status: Optional[str] = "ACTIVE"

class EmployeeUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department_id: Optional[str] = None
    status: Optional[str] = None

class AssignDeviceRequest(BaseModel):
    device_id: str = Field(...)
