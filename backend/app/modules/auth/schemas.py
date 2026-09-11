from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=3, description="Username or email address")
    password: str = Field(..., min_length=4, description="User password")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="JWT refresh token")

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(...)
    new_password: str = Field(..., min_length=8)
