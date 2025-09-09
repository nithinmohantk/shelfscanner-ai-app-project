"""
Session Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
import secrets
import string
from datetime import datetime, timezone, timedelta

from app.core.database import get_database
from app.core.config import settings
from app.models.user import UserSession
from app.schemas.user import SessionCreate, SessionResponse, SessionUpdate

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def generate_session_id() -> str:
    """Generate a secure session ID"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))


@router.post("/", response_model=SessionResponse)
@limiter.limit("10/minute")
async def create_session(
    request: Request,
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new user session"""
    try:
        # Generate session ID and expiration
        session_id = generate_session_id()
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.SESSION_TIMEOUT)
        
        # Get client info
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent")
        
        # Create session
        new_session = UserSession(
            session_id=session_id,
            device_id=session_data.device_id,
            user_agent=user_agent or session_data.user_agent,
            ip_address=client_ip,
            name=session_data.name,
            email=session_data.email,
            expires_at=expires_at
        )
        
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        
        return SessionResponse(
            id=str(new_session.id),
            session_id=new_session.session_id,
            device_id=new_session.device_id,
            name=new_session.name,
            email=new_session.email,
            is_active=new_session.is_active,
            created_at=new_session.created_at,
            expires_at=new_session.expires_at,
            last_activity=new_session.last_activity
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating session: {str(e)}")


@router.get("/{session_id}", response_model=SessionResponse)
@limiter.limit("30/minute")
async def get_session(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get session by ID"""
    try:
        result = await db.execute(select(UserSession).where(UserSession.session_id == session_id))
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.is_expired:
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Update last activity
        session.last_activity = datetime.now(timezone.utc)
        await db.commit()
        
        return SessionResponse(
            id=str(session.id),
            session_id=session.session_id,
            device_id=session.device_id,
            name=session.name,
            email=session.email,
            is_active=session.is_active,
            created_at=session.created_at,
            expires_at=session.expires_at,
            last_activity=session.last_activity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")


@router.put("/{session_id}", response_model=SessionResponse)
@limiter.limit("20/minute")
async def update_session(
    request: Request,
    session_id: str,
    session_data: SessionUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update session data"""
    try:
        result = await db.execute(select(UserSession).where(UserSession.session_id == session_id))
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.is_expired:
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Update fields
        if session_data.name is not None:
            session.name = session_data.name
        if session_data.email is not None:
            session.email = session_data.email
        
        session.last_activity = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(session)
        
        return SessionResponse(
            id=str(session.id),
            session_id=session.session_id,
            device_id=session.device_id,
            name=session.name,
            email=session.email,
            is_active=session.is_active,
            created_at=session.created_at,
            expires_at=session.expires_at,
            last_activity=session.last_activity
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating session: {str(e)}")


@router.delete("/{session_id}")
@limiter.limit("10/minute")
async def delete_session(
    request: Request,
    session_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Delete/deactivate session"""
    try:
        result = await db.execute(select(UserSession).where(UserSession.session_id == session_id))
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Deactivate instead of delete to preserve data
        session.is_active = False
        await db.commit()
        
        return {"message": "Session deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")
