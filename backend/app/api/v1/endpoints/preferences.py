"""
User Preferences API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.database import get_database
from app.models.user import UserSession
from app.models.preference import UserPreference
from app.schemas.preference import PreferenceCreate, PreferenceUpdate, PreferenceResponse, GoodreadsImportRequest

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/", response_model=PreferenceResponse)
@limiter.limit("10/minute")
async def create_preferences(
    request: Request,
    preference_data: PreferenceCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create user preferences"""
    try:
        # Verify session exists
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == preference_data.session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if preferences already exist
        existing_result = await db.execute(
            select(UserPreference).where(UserPreference.session_id == session.id)
        )
        existing_prefs = existing_result.scalar_one_or_none()
        
        if existing_prefs:
            raise HTTPException(status_code=400, detail="Preferences already exist for this session")
        
        # Create new preferences
        new_prefs = UserPreference(
            session_id=session.id,
            favorite_genres=preference_data.favorite_genres,
            disliked_genres=preference_data.disliked_genres,
            favorite_authors=preference_data.favorite_authors,
            reading_goals=preference_data.reading_goals,
            preferred_length=preference_data.preferred_length,
            preferred_publication_era=preference_data.preferred_publication_era,
            content_preferences=preference_data.content_preferences,
            reading_frequency=preference_data.reading_frequency,
            reading_time=preference_data.reading_time,
            preferred_format=preference_data.preferred_format,
            reading_experience=preference_data.reading_experience,
            language_preferences=preference_data.language_preferences,
            recommendation_style=preference_data.recommendation_style,
            discovery_openness=preference_data.discovery_openness,
            goodreads_user_id=preference_data.goodreads_user_id,
            reading_history=preference_data.reading_history
        )
        
        db.add(new_prefs)
        await db.commit()
        await db.refresh(new_prefs)
        
        return PreferenceResponse(
            id=str(new_prefs.id),
            session_id=preference_data.session_id,
            favorite_genres=new_prefs.favorite_genres or [],
            disliked_genres=new_prefs.disliked_genres or [],
            favorite_authors=new_prefs.favorite_authors or [],
            reading_goals=new_prefs.reading_goals or {},
            preferred_length=new_prefs.preferred_length,
            preferred_publication_era=new_prefs.preferred_publication_era,
            content_preferences=new_prefs.content_preferences or {},
            reading_frequency=new_prefs.reading_frequency,
            reading_time=new_prefs.reading_time,
            preferred_format=new_prefs.preferred_format,
            reading_experience=new_prefs.reading_experience,
            language_preferences=new_prefs.language_preferences or ["en"],
            recommendation_style=new_prefs.recommendation_style,
            discovery_openness=new_prefs.discovery_openness,
            reading_history=new_prefs.reading_history or [],
            created_at=new_prefs.created_at,
            updated_at=new_prefs.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating preferences: {str(e)}")


@router.get("/{session_id}", response_model=PreferenceResponse)
@limiter.limit("30/minute")
async def get_preferences(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get user preferences by session ID"""
    try:
        # Get session
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get preferences
        prefs_result = await db.execute(
            select(UserPreference).where(UserPreference.session_id == session.id)
        )
        prefs = prefs_result.scalar_one_or_none()
        
        if not prefs:
            raise HTTPException(status_code=404, detail="Preferences not found")
        
        return PreferenceResponse(
            id=str(prefs.id),
            session_id=session_id,
            favorite_genres=prefs.favorite_genres or [],
            disliked_genres=prefs.disliked_genres or [],
            favorite_authors=prefs.favorite_authors or [],
            reading_goals=prefs.reading_goals or {},
            preferred_length=prefs.preferred_length,
            preferred_publication_era=prefs.preferred_publication_era,
            content_preferences=prefs.content_preferences or {},
            reading_frequency=prefs.reading_frequency,
            reading_time=prefs.reading_time,
            preferred_format=prefs.preferred_format,
            reading_experience=prefs.reading_experience,
            language_preferences=prefs.language_preferences or ["en"],
            recommendation_style=prefs.recommendation_style,
            discovery_openness=prefs.discovery_openness,
            reading_history=prefs.reading_history or [],
            created_at=prefs.created_at,
            updated_at=prefs.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving preferences: {str(e)}")


@router.put("/{session_id}", response_model=PreferenceResponse)
@limiter.limit("20/minute")
async def update_preferences(
    request: Request,
    session_id: str,
    preference_data: PreferenceUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update user preferences"""
    try:
        # Get session
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get preferences
        prefs_result = await db.execute(
            select(UserPreference).where(UserPreference.session_id == session.id)
        )
        prefs = prefs_result.scalar_one_or_none()
        
        if not prefs:
            raise HTTPException(status_code=404, detail="Preferences not found")
        
        # Update fields
        update_fields = preference_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            setattr(prefs, field, value)
        
        await db.commit()
        await db.refresh(prefs)
        
        return PreferenceResponse(
            id=str(prefs.id),
            session_id=session_id,
            favorite_genres=prefs.favorite_genres or [],
            disliked_genres=prefs.disliked_genres or [],
            favorite_authors=prefs.favorite_authors or [],
            reading_goals=prefs.reading_goals or {},
            preferred_length=prefs.preferred_length,
            preferred_publication_era=prefs.preferred_publication_era,
            content_preferences=prefs.content_preferences or {},
            reading_frequency=prefs.reading_frequency,
            reading_time=prefs.reading_time,
            preferred_format=prefs.preferred_format,
            reading_experience=prefs.reading_experience,
            language_preferences=prefs.language_preferences or ["en"],
            recommendation_style=prefs.recommendation_style,
            discovery_openness=prefs.discovery_openness,
            reading_history=prefs.reading_history or [],
            created_at=prefs.created_at,
            updated_at=prefs.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


@router.post("/import-goodreads")
@limiter.limit("5/minute")
async def import_goodreads_data(
    request: Request,
    import_data: GoodreadsImportRequest,
    db: AsyncSession = Depends(get_database)
):
    """Import Goodreads data and update preferences"""
    try:
        # Get session
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == import_data.session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get or create preferences
        prefs_result = await db.execute(
            select(UserPreference).where(UserPreference.session_id == session.id)
        )
        prefs = prefs_result.scalar_one_or_none()
        
        if not prefs:
            prefs = UserPreference(session_id=session.id)
            db.add(prefs)
        
        # Process Goodreads data (simplified - would need more complex parsing)
        goodreads_data = import_data.goodreads_data
        
        # Update preferences with Goodreads data
        prefs.goodreads_user_id = import_data.goodreads_user_id
        prefs.goodreads_data = goodreads_data
        
        # Extract reading history if available
        if "books" in goodreads_data:
            reading_history = []
            for book in goodreads_data["books"][:100]:  # Limit to recent 100 books
                reading_history.append({
                    "title": book.get("title", ""),
                    "author": book.get("author", ""),
                    "rating": book.get("rating"),
                    "date_read": book.get("date_read"),
                    "review": book.get("review", "")
                })
            
            if import_data.merge_with_existing and prefs.reading_history:
                prefs.reading_history.extend(reading_history)
            else:
                prefs.reading_history = reading_history
        
        await db.commit()
        await db.refresh(prefs)
        
        return {"message": "Goodreads data imported successfully", "books_imported": len(prefs.reading_history or [])}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing Goodreads data: {str(e)}")
