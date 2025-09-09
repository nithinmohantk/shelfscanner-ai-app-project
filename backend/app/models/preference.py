"""
User Preference Models
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class UserPreference(Base):
    """
    User preference model for storing reading preferences and history
    """
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=False, index=True)
    
    # Reading preferences
    favorite_genres = Column(JSON, nullable=True)  # List of favorite genres
    disliked_genres = Column(JSON, nullable=True)  # List of disliked genres
    favorite_authors = Column(JSON, nullable=True)  # List of favorite authors
    reading_goals = Column(JSON, nullable=True)  # Reading goals (books per year, etc.)
    
    # Book characteristics preferences
    preferred_length = Column(String(20), nullable=True)  # short, medium, long, any
    preferred_publication_era = Column(String(50), nullable=True)  # classic, modern, contemporary, any
    content_preferences = Column(JSON, nullable=True)  # violence, romance, etc. preferences
    
    # Reading habits
    reading_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly, occasional
    reading_time = Column(String(20), nullable=True)  # morning, afternoon, evening, night
    preferred_format = Column(String(20), nullable=True)  # physical, ebook, audiobook, any
    
    # Experience level
    reading_experience = Column(String(20), nullable=True)  # beginner, intermediate, advanced, expert
    language_preferences = Column(JSON, nullable=True)  # Preferred languages
    
    # Goodreads integration
    goodreads_user_id = Column(String(50), nullable=True)
    goodreads_data = Column(JSON, nullable=True)  # Imported Goodreads data
    reading_history = Column(JSON, nullable=True)  # Previously read books
    
    # Recommendation tuning
    recommendation_style = Column(String(30), nullable=True)  # conservative, adventurous, mixed
    discovery_openness = Column(Float, nullable=True)  # 0.0-1.0 how open to new genres/authors
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    last_goodreads_sync = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("UserSession", back_populates="preferences")
    
    def __repr__(self):
        return f"<UserPreference(session_id={self.session_id}, genres={self.favorite_genres})>"
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            "id": str(self.id),
            "favorite_genres": self.favorite_genres or [],
            "disliked_genres": self.disliked_genres or [],
            "favorite_authors": self.favorite_authors or [],
            "reading_goals": self.reading_goals or {},
            "preferred_length": self.preferred_length,
            "preferred_publication_era": self.preferred_publication_era,
            "content_preferences": self.content_preferences or {},
            "reading_frequency": self.reading_frequency,
            "reading_time": self.reading_time,
            "preferred_format": self.preferred_format,
            "reading_experience": self.reading_experience,
            "language_preferences": self.language_preferences or ["en"],
            "recommendation_style": self.recommendation_style,
            "discovery_openness": self.discovery_openness,
            "reading_history": self.reading_history or [],
        }
