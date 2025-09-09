"""
Book Recommendation API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List

from app.core.database import get_database
from app.models.user import UserSession
from app.models.book import Book, BookRecommendation
from app.models.preference import UserPreference
from app.schemas.book import RecommendationRequest, BookRecommendationResponse, BookInteractionRequest
from app.services.ai.openai_service import OpenAIVisionService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate", response_model=List[BookRecommendationResponse])
@limiter.limit("10/minute")
async def generate_recommendations(
    request: Request,
    rec_request: RecommendationRequest,
    db: AsyncSession = Depends(get_database)
):
    """Generate book recommendations for a user"""
    try:
        # Verify session
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == rec_request.session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.is_expired:
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Get user preferences
        prefs_result = await db.execute(
            select(UserPreference).where(UserPreference.session_id == session.id)
        )
        user_preferences = prefs_result.scalar_one_or_none()
        
        if not user_preferences:
            raise HTTPException(status_code=404, detail="User preferences not found")
        
        # For demo purposes, create some mock recognized books if shelf_scan_id provided
        recognized_books = []
        if rec_request.shelf_scan_id:
            # In a real implementation, you'd fetch the actual scan results
            recognized_books = [
                {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "confidence": 0.9},
                {"title": "To Kill a Mockingbird", "author": "Harper Lee", "confidence": 0.8},
                {"title": "1984", "author": "George Orwell", "confidence": 0.95}
            ]
        
        # Use OpenAI service to generate recommendations
        openai_service = OpenAIVisionService()
        
        # Convert user preferences to dict format
        preferences_dict = user_preferences.to_dict()
        
        try:
            ai_recommendations = await openai_service.get_book_recommendations(
                preferences_dict,
                recognized_books,
                rec_request.max_recommendations
            )
        except Exception as e:
            # Fallback to manual recommendations if AI fails
            ai_recommendations = _get_fallback_recommendations(preferences_dict, rec_request.max_recommendations)
        
        # Save recommendations to database and return response
        recommendations = []
        for ai_rec in ai_recommendations:
            # Check if book already exists in database
            book_result = await db.execute(
                select(Book).where(Book.title == ai_rec["title"])
            )
            book = book_result.scalar_one_or_none()
            
            # Create book if it doesn't exist
            if not book:
                book = Book(
                    title=ai_rec["title"],
                    author=ai_rec.get("author"),
                    genre=ai_rec.get("genre"),
                    publication_year=ai_rec.get("publication_year"),
                    source="ai_recommendation",
                    confidence_score=ai_rec.get("appeal_score", 0.5)
                )
                db.add(book)
                await db.flush()  # Get the book ID without committing
            
            # Create recommendation record
            recommendation = BookRecommendation(
                session_id=session.id,
                book_id=book.id,
                reason=ai_rec.get("reason", "AI recommended based on your preferences"),
                score=ai_rec.get("appeal_score", 0.5),
                source_books=[ai_rec.get("similarity_to")] if ai_rec.get("similarity_to") else [],
                shelf_scan_id=rec_request.shelf_scan_id,
                recommendation_type="ai"
            )
            db.add(recommendation)
            
            recommendations.append(BookRecommendationResponse(
                id=str(recommendation.id) if hasattr(recommendation, 'id') else "pending",
                book=book.to_dict(),
                reason=recommendation.reason,
                score=recommendation.score,
                source_books=recommendation.source_books,
                recommendation_type=recommendation.recommendation_type,
                is_saved=recommendation.is_saved,
                created_at=recommendation.created_at or "pending"
            ))
        
        await db.commit()
        
        # Refresh recommendations to get proper IDs and timestamps
        for i, rec in enumerate(recommendations):
            if rec.id == "pending":
                await db.refresh(recommendation)
                rec.id = str(recommendation.id)
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.get("/{session_id}", response_model=List[BookRecommendationResponse])
@limiter.limit("30/minute")
async def get_recommendations(
    request: Request,
    session_id: str,
    limit: int = 20,
    db: AsyncSession = Depends(get_database)
):
    """Get existing recommendations for a user"""
    try:
        # Verify session
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get recommendations
        recs_result = await db.execute(
            select(BookRecommendation, Book)
            .join(Book, BookRecommendation.book_id == Book.id)
            .where(BookRecommendation.session_id == session.id)
            .order_by(BookRecommendation.created_at.desc())
            .limit(limit)
        )
        
        recommendations = []
        for rec, book in recs_result:
            recommendations.append(BookRecommendationResponse(
                id=str(rec.id),
                book=book.to_dict(),
                reason=rec.reason,
                score=rec.score,
                source_books=rec.source_books,
                recommendation_type=rec.recommendation_type,
                is_saved=rec.is_saved,
                created_at=rec.created_at
            ))
        
        return recommendations
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving recommendations: {str(e)}")


@router.post("/interaction")
@limiter.limit("50/minute")
async def track_interaction(
    request: Request,
    interaction: BookInteractionRequest,
    db: AsyncSession = Depends(get_database)
):
    """Track user interaction with a recommendation"""
    try:
        # Get recommendation
        rec_result = await db.execute(
            select(BookRecommendation).where(BookRecommendation.id == interaction.recommendation_id)
        )
        recommendation = rec_result.scalar_one_or_none()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # Update recommendation based on interaction type
        if interaction.interaction_type == "viewed":
            from datetime import datetime, timezone
            recommendation.viewed_at = datetime.now(timezone.utc)
        elif interaction.interaction_type == "saved":
            recommendation.is_saved = True
        elif interaction.interaction_type == "interested":
            recommendation.is_interested = True
        elif interaction.interaction_type == "purchased":
            recommendation.is_purchased = True
        
        await db.commit()
        
        return {"message": f"Interaction '{interaction.interaction_type}' tracked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking interaction: {str(e)}")


def _get_fallback_recommendations(preferences: dict, max_recommendations: int) -> List[dict]:
    """Fallback recommendations when AI service fails"""
    # Simple fallback based on popular books in user's preferred genres
    fallback_books = [
        {
            "title": "The Seven Husbands of Evelyn Hugo",
            "author": "Taylor Jenkins Reid",
            "reason": "Popular contemporary fiction with compelling characters",
            "appeal_score": 0.8,
            "genre": "Contemporary Fiction",
            "publication_year": 2017
        },
        {
            "title": "Educated",
            "author": "Tara Westover",
            "reason": "Critically acclaimed memoir about education and family",
            "appeal_score": 0.9,
            "genre": "Memoir",
            "publication_year": 2018
        },
        {
            "title": "The Midnight Library",
            "author": "Matt Haig",
            "reason": "Thought-provoking fiction about life choices",
            "appeal_score": 0.75,
            "genre": "Literary Fiction",
            "publication_year": 2020
        },
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "reason": "Popular self-improvement book about building good habits",
            "appeal_score": 0.85,
            "genre": "Self-Help",
            "publication_year": 2018
        },
        {
            "title": "The Song of Achilles",
            "author": "Madeline Miller",
            "reason": "Beautifully written retelling of Greek mythology",
            "appeal_score": 0.8,
            "genre": "Historical Fiction",
            "publication_year": 2011
        }
    ]
    
    # Filter based on user preferences if available
    if preferences.get("favorite_genres"):
        user_genres = [genre.lower() for genre in preferences["favorite_genres"]]
        fallback_books = [
            book for book in fallback_books 
            if any(genre in book["genre"].lower() for genre in user_genres)
        ]
    
    # If no matches with user preferences, return the original list
    if not fallback_books:
        fallback_books = [
            {
                "title": "The Seven Husbands of Evelyn Hugo",
                "author": "Taylor Jenkins Reid",
                "reason": "Popular contemporary fiction",
                "appeal_score": 0.8,
                "genre": "Contemporary Fiction",
                "publication_year": 2017
            }
        ]
    
    return fallback_books[:max_recommendations]
