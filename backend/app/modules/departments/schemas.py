from typing import Optional
from pydantic import BaseModel, Field

class DepartmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    manager_id: Optional[str] = None

class DepartmentUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    manager_id: Optional[str] = None
