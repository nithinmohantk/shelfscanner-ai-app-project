"""
User Preference Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PreferenceCreate(BaseModel):
    """Schema for creating user preferences"""
    session_id: str = Field(..., description="User session ID")
    favorite_genres: Optional[List[str]] = Field(None, description="Favorite genres")
    disliked_genres: Optional[List[str]] = Field(None, description="Disliked genres")
    favorite_authors: Optional[List[str]] = Field(None, description="Favorite authors")
    reading_goals: Optional[Dict[str, Any]] = Field(None, description="Reading goals")
    preferred_length: Optional[str] = Field(None, description="Preferred book length")
    preferred_publication_era: Optional[str] = Field(None, description="Preferred publication era")
    content_preferences: Optional[Dict[str, Any]] = Field(None, description="Content preferences")
    reading_frequency: Optional[str] = Field(None, description="Reading frequency")
    reading_time: Optional[str] = Field(None, description="Preferred reading time")
    preferred_format: Optional[str] = Field(None, description="Preferred book format")
    reading_experience: Optional[str] = Field(None, description="Reading experience level")
    language_preferences: Optional[List[str]] = Field(None, description="Preferred languages")
    recommendation_style: Optional[str] = Field(None, description="Recommendation style")
    discovery_openness: Optional[float] = Field(None, ge=0, le=1, description="Openness to discovery")
    goodreads_user_id: Optional[str] = Field(None, description="Goodreads user ID")
    reading_history: Optional[List[Dict[str, Any]]] = Field(None, description="Reading history")


class PreferenceUpdate(BaseModel):
    """Schema for updating user preferences"""
    favorite_genres: Optional[List[str]] = Field(None, description="Favorite genres")
    disliked_genres: Optional[List[str]] = Field(None, description="Disliked genres")
    favorite_authors: Optional[List[str]] = Field(None, description="Favorite authors")
    reading_goals: Optional[Dict[str, Any]] = Field(None, description="Reading goals")
    preferred_length: Optional[str] = Field(None, description="Preferred book length")
    preferred_publication_era: Optional[str] = Field(None, description="Preferred publication era")
    content_preferences: Optional[Dict[str, Any]] = Field(None, description="Content preferences")
    reading_frequency: Optional[str] = Field(None, description="Reading frequency")
    reading_time: Optional[str] = Field(None, description="Preferred reading time")
    preferred_format: Optional[str] = Field(None, description="Preferred book format")
    reading_experience: Optional[str] = Field(None, description="Reading experience level")
    language_preferences: Optional[List[str]] = Field(None, description="Preferred languages")
    recommendation_style: Optional[str] = Field(None, description="Recommendation style")
    discovery_openness: Optional[float] = Field(None, ge=0, le=1, description="Openness to discovery")
    goodreads_user_id: Optional[str] = Field(None, description="Goodreads user ID")
    reading_history: Optional[List[Dict[str, Any]]] = Field(None, description="Reading history")


class PreferenceResponse(BaseModel):
    """Schema for preference response"""
    id: str = Field(..., description="Preference UUID")
    session_id: str = Field(..., description="Session ID")
    favorite_genres: List[str] = Field(..., description="Favorite genres")
    disliked_genres: List[str] = Field(..., description="Disliked genres")
    favorite_authors: List[str] = Field(..., description="Favorite authors")
    reading_goals: Dict[str, Any] = Field(..., description="Reading goals")
    preferred_length: Optional[str] = Field(None, description="Preferred book length")
    preferred_publication_era: Optional[str] = Field(None, description="Preferred publication era")
    content_preferences: Dict[str, Any] = Field(..., description="Content preferences")
    reading_frequency: Optional[str] = Field(None, description="Reading frequency")
    reading_time: Optional[str] = Field(None, description="Preferred reading time")
    preferred_format: Optional[str] = Field(None, description="Preferred book format")
    reading_experience: Optional[str] = Field(None, description="Reading experience level")
    language_preferences: List[str] = Field(..., description="Preferred languages")
    recommendation_style: Optional[str] = Field(None, description="Recommendation style")
    discovery_openness: Optional[float] = Field(None, description="Openness to discovery")
    reading_history: List[Dict[str, Any]] = Field(..., description="Reading history")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class GoodreadsImportRequest(BaseModel):
    """Schema for Goodreads data import"""
    session_id: str = Field(..., description="User session ID")
    goodreads_user_id: Optional[str] = Field(None, description="Goodreads user ID")
    goodreads_data: Dict[str, Any] = Field(..., description="Goodreads export data")
    merge_with_existing: bool = Field(True, description="Merge with existing preferences")
