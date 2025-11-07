from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """Schema for user registration"""
    identifier: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)

    @field_validator('identifier')
    @classmethod
    def validate_identifier(cls, v):
        if not v or v.strip() == "":
            raise ValueError('Identifier cannot be empty')
        return v.strip()


class UserLogin(BaseModel):
    """Schema for user login"""
    identifier: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=100)


class TokenResponse(BaseModel):
    """OAuth2.0 compliant token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    """Schema for token refresh"""
    refresh_token: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    identifier: str
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AvatarUploadResponse(BaseModel):
    """Schema for avatar upload response"""
    avatar_url: str


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages"""
    type: str
    user_id: int
    avatar_url: str
    timestamp: datetime