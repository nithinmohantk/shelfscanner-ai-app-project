"""
Shelf Scan API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from slowapi import Limiter
from slowapi.util import get_remote_address
import uuid
import os
import time
from PIL import Image
import io

from app.core.database import get_database
from app.core.config import settings
from app.models.user import UserSession
from app.schemas.book import ShelfScanResponse, RecognizedBook
from app.services.ai.openai_service import OpenAIVisionService
from app.services.ai.google_vision_service import GoogleVisionService

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def validate_image(file: UploadFile) -> bool:
    """Validate uploaded image file"""
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        return False
    
    if file.size > settings.MAX_FILE_SIZE:
        return False
    
    return True


def save_uploaded_image(file: UploadFile, scan_id: str) -> str:
    """Save uploaded image and return file path"""
    # Create scan-specific directory
    scan_dir = os.path.join(settings.UPLOAD_PATH, scan_id)
    os.makedirs(scan_dir, exist_ok=True)
    
    # Generate filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f"shelf_image.{file_extension}"
    file_path = os.path.join(scan_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())
    
    return file_path


@router.post("/shelf", response_model=ShelfScanResponse)
@limiter.limit("5/minute")
async def scan_shelf(
    request: Request,
    session_id: str = Form(...),
    use_fallback: bool = Form(True),
    max_books: int = Form(20),
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_database)
):
    """Scan bookshelf image and identify books"""
    start_time = time.time()
    scan_id = str(uuid.uuid4())
    
    try:
        # Validate session
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.is_expired:
            raise HTTPException(status_code=401, detail="Session expired")
        
        # Validate image
        if not validate_image(image):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image. Must be {', '.join(settings.ALLOWED_IMAGE_TYPES)} and under {settings.MAX_FILE_SIZE / (1024*1024)}MB"
            )
        
        # Save image
        image_path = save_uploaded_image(image, scan_id)
        
        # Initialize AI services
        openai_service = OpenAIVisionService()
        google_service = GoogleVisionService() if use_fallback else None
        
        recognized_books = []
        api_used = "none"
        error_message = None
        success = False
        
        try:
            # Try OpenAI first
            if settings.OPENAI_API_KEY:
                try:
                    books = await openai_service.identify_books(image_path, max_books)
                    recognized_books = [
                        RecognizedBook(
                            title=book["title"],
                            author=book.get("author"),
                            confidence=book.get("confidence", 0.0),
                            position=book.get("position")
                        ) for book in books
                    ]
                    api_used = "openai"
                    success = True
                except Exception as e:
                    error_message = f"OpenAI failed: {str(e)}"
                    if not use_fallback:
                        raise
            
            # Try Google Vision as fallback
            if not success and use_fallback and google_service and settings.GOOGLE_CLOUD_PROJECT:
                try:
                    books = await google_service.identify_books(image_path, max_books)
                    recognized_books = [
                        RecognizedBook(
                            title=book["title"],
                            author=book.get("author"),
                            confidence=book.get("confidence", 0.0),
                            position=book.get("position")
                        ) for book in books
                    ]
                    api_used = "google"
                    success = True
                except Exception as e:
                    error_message = f"Google Vision also failed: {str(e)}"
            
            if not success:
                raise HTTPException(
                    status_code=500, 
                    detail=error_message or "Both AI services failed"
                )
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")
        
        processing_time = time.time() - start_time
        
        return ShelfScanResponse(
            scan_id=scan_id,
            recognized_books=recognized_books,
            total_books_found=len(recognized_books),
            processing_time=processing_time,
            api_used=api_used,
            success=success,
            error_message=error_message if not success else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        return ShelfScanResponse(
            scan_id=scan_id,
            recognized_books=[],
            total_books_found=0,
            processing_time=processing_time,
            api_used="none",
            success=False,
            error_message=f"Scan failed: {str(e)}"
        )


@router.get("/history/{session_id}")
@limiter.limit("10/minute")
async def get_scan_history(
    request: Request,
    session_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_database)
):
    """Get scan history for a session"""
    try:
        # Verify session
        session_result = await db.execute(
            select(UserSession).where(UserSession.session_id == session_id)
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # For now, return empty list - would need to implement scan history storage
        return {
            "scans": [],
            "total": 0,
            "message": "Scan history feature coming soon"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving scan history: {str(e)}")


@router.delete("/cleanup/{scan_id}")
@limiter.limit("10/minute")
async def cleanup_scan_data(
    request: Request,
    scan_id: str
):
    """Clean up uploaded images and temporary data for a scan"""
    try:
        scan_dir = os.path.join(settings.UPLOAD_PATH, scan_id)
        
        if os.path.exists(scan_dir):
            import shutil
            shutil.rmtree(scan_dir)
            return {"message": f"Scan data for {scan_id} cleaned up successfully"}
        else:
            return {"message": "Scan data not found or already cleaned up"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up scan data: {str(e)}")
