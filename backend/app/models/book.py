"""
Book Models
"""

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Book(Base):
    """
    Book model for storing book metadata
    """
    __tablename__ = "books"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(300), nullable=True, index=True)
    isbn = Column(String(20), nullable=True, unique=True, index=True)
    isbn13 = Column(String(20), nullable=True, unique=True, index=True)
    
    # Book details
    description = Column(Text, nullable=True)
    publication_year = Column(Integer, nullable=True)
    publisher = Column(String(200), nullable=True)
    language = Column(String(10), nullable=True, default="en")
    page_count = Column(Integer, nullable=True)
    
    # Categorization
    genre = Column(String(100), nullable=True)
    categories = Column(JSON, nullable=True)  # List of categories
    tags = Column(JSON, nullable=True)  # List of tags
    
    # Ratings and popularity
    average_rating = Column(Float, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    goodreads_id = Column(String(50), nullable=True, index=True)
    
    # External links
    cover_url = Column(String(500), nullable=True)
    amazon_url = Column(String(500), nullable=True)
    goodreads_url = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    
    # Source tracking
    source = Column(String(50), nullable=True)  # Where book data came from (OpenAI, Google Books, etc.)
    confidence_score = Column(Float, nullable=True)  # Confidence in book identification
    
    # Relationships
    recommendations = relationship("BookRecommendation", back_populates="book", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}')>"
    
    def to_dict(self):
        """Convert book to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "isbn13": self.isbn13,
            "description": self.description,
            "publication_year": self.publication_year,
            "publisher": self.publisher,
            "language": self.language,
            "page_count": self.page_count,
            "genre": self.genre,
            "categories": self.categories,
            "tags": self.tags,
            "average_rating": self.average_rating,
            "ratings_count": self.ratings_count,
            "cover_url": self.cover_url,
            "amazon_url": self.amazon_url,
            "goodreads_url": self.goodreads_url,
            "confidence_score": self.confidence_score,
        }


class BookRecommendation(Base):
    """
    Book recommendation model linking sessions to recommended books
    """
    __tablename__ = "book_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("user_sessions.id"), nullable=False, index=True)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id"), nullable=False, index=True)
    
    # Recommendation details
    reason = Column(Text, nullable=True)  # Why this book was recommended
    score = Column(Float, nullable=True)  # Recommendation strength (0.0 - 1.0)
    source_books = Column(JSON, nullable=True)  # Books that led to this recommendation
    
    # User interaction
    is_interested = Column(Boolean, nullable=True)  # User marked as interested
    is_saved = Column(Boolean, default=False)  # User saved for later
    is_purchased = Column(Boolean, default=False)  # User clicked purchase
    viewed_at = Column(DateTime(timezone=True), nullable=True)  # When user viewed details
    
    # Recommendation context
    shelf_scan_id = Column(String(100), nullable=True, index=True)  # Link to specific shelf scan
    recommendation_type = Column(String(50), nullable=False, default="ai")  # ai, similar, popular, etc.
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    
    # Relationships
    session = relationship("UserSession", back_populates="recommendations")
    book = relationship("Book", back_populates="recommendations")
    
    def __repr__(self):
        return f"<BookRecommendation(book='{self.book.title if self.book else 'Unknown'}', score={self.score})>"
