"""
Book and Recommendation Schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class BookResponse(BaseModel):
    """Schema for book response"""
    id: str = Field(..., description="Book UUID")
    title: str = Field(..., description="Book title")
    author: Optional[str] = Field(None, description="Book author")
    isbn: Optional[str] = Field(None, description="ISBN-10")
    isbn13: Optional[str] = Field(None, description="ISBN-13")
    description: Optional[str] = Field(None, description="Book description")
    publication_year: Optional[int] = Field(None, description="Publication year")
    publisher: Optional[str] = Field(None, description="Publisher")
    language: Optional[str] = Field(None, description="Book language")
    page_count: Optional[int] = Field(None, description="Number of pages")
    genre: Optional[str] = Field(None, description="Primary genre")
    categories: Optional[List[str]] = Field(None, description="Categories/genres")
    tags: Optional[List[str]] = Field(None, description="Tags")
    average_rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating")
    ratings_count: Optional[int] = Field(None, ge=0, description="Number of ratings")
    cover_url: Optional[str] = Field(None, description="Cover image URL")
    amazon_url: Optional[str] = Field(None, description="Amazon purchase URL")
    goodreads_url: Optional[str] = Field(None, description="Goodreads URL")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="AI confidence score")
    
    class Config:
        from_attributes = True


class BookRecommendationResponse(BaseModel):
    """Schema for book recommendation response"""
    id: str = Field(..., description="Recommendation UUID")
    book: BookResponse = Field(..., description="Recommended book")
    reason: Optional[str] = Field(None, description="Recommendation reason")
    score: Optional[float] = Field(None, ge=0, le=1, description="Recommendation score")
    source_books: Optional[List[str]] = Field(None, description="Source books that led to recommendation")
    recommendation_type: str = Field(..., description="Type of recommendation")
    is_saved: bool = Field(False, description="User saved status")
    created_at: datetime = Field(..., description="Recommendation creation time")
    
    class Config:
        from_attributes = True


class ShelfScanRequest(BaseModel):
    """Schema for shelf scan request"""
    session_id: str = Field(..., description="User session ID")
    use_fallback: bool = Field(True, description="Use Google Vision API as fallback")
    max_books: int = Field(20, ge=1, le=50, description="Maximum books to identify")
    

class RecognizedBook(BaseModel):
    """Schema for a book recognized from shelf scan"""
    title: str = Field(..., description="Recognized book title")
    author: Optional[str] = Field(None, description="Recognized author")
    confidence: float = Field(..., ge=0, le=1, description="Recognition confidence")
    position: Optional[Dict[str, Any]] = Field(None, description="Position in image")


class ShelfScanResponse(BaseModel):
    """Schema for shelf scan response"""
    scan_id: str = Field(..., description="Unique scan identifier")
    recognized_books: List[RecognizedBook] = Field(..., description="Books recognized from image")
    total_books_found: int = Field(..., description="Total number of books found")
    processing_time: float = Field(..., description="Processing time in seconds")
    api_used: str = Field(..., description="AI API used (openai/google)")
    success: bool = Field(..., description="Scan success status")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class RecommendationRequest(BaseModel):
    """Schema for recommendation request"""
    session_id: str = Field(..., description="User session ID")
    shelf_scan_id: Optional[str] = Field(None, description="Shelf scan ID for context")
    max_recommendations: int = Field(10, ge=1, le=20, description="Maximum recommendations")
    include_similar: bool = Field(True, description="Include similar book recommendations")
    include_new: bool = Field(True, description="Include new/different genre recommendations")


class BookInteractionRequest(BaseModel):
    """Schema for tracking book interactions"""
    recommendation_id: str = Field(..., description="Recommendation ID")
    interaction_type: str = Field(..., description="Type of interaction: viewed, saved, interested, purchased")
    additional_data: Optional[Dict[str, Any]] = Field(None, description="Additional interaction data")
