"""
User Session Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class SessionCreate(BaseModel):
    """Schema for creating a new session"""
    device_id: Optional[str] = Field(None, description="Device identifier")
    user_agent: Optional[str] = Field(None, description="Browser user agent")
    name: Optional[str] = Field(None, max_length=100, description="Optional display name")
    email: Optional[str] = Field(None, description="Optional email for Goodreads import")


class SessionResponse(BaseModel):
    """Schema for session response"""
    id: str = Field(..., description="Session UUID")
    session_id: str = Field(..., description="Session identifier")
    device_id: Optional[str] = Field(None, description="Device identifier")
    name: Optional[str] = Field(None, description="Display name")
    email: Optional[str] = Field(None, description="Email address")
    is_active: bool = Field(..., description="Session active status")
    created_at: datetime = Field(..., description="Session creation time")
    expires_at: datetime = Field(..., description="Session expiration time")
    last_activity: datetime = Field(..., description="Last activity time")
    
    class Config:
        from_attributes = True


class SessionUpdate(BaseModel):
    """Schema for updating session data"""
    name: Optional[str] = Field(None, max_length=100, description="Display name")
    email: Optional[str] = Field(None, description="Email address")
