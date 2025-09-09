"""
User and Session Models
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class UserSession(Base):
    """
    User session model for device-based session management
    No user accounts - just sessions tied to devices
    """
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    device_id = Column(String(255), index=True, nullable=True)  # Browser fingerprint or device ID
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    
    # Session status
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Optional user data
    name = Column(String(100), nullable=True)  # Optional display name
    email = Column(String(255), nullable=True)  # Optional for Goodreads import
    
    # Relationships
    preferences = relationship("UserPreference", back_populates="session", cascade="all, delete-orphan")
    recommendations = relationship("BookRecommendation", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserSession(session_id={self.session_id}, active={self.is_active})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
