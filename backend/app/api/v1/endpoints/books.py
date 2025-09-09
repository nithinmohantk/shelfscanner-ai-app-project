"""
Books API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List, Optional

from app.core.database import get_database
from app.models.book import Book
from app.schemas.book import BookResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/search", response_model=List[BookResponse])
@limiter.limit("30/minute")
async def search_books(
    request: Request,
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, le=50, description="Maximum results to return"),
    db: AsyncSession = Depends(get_database)
):
    """Search books by title, author, or other metadata"""
    try:
        if len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        search_term = f"%{q.strip()}%"
        
        # Search in title and author fields
        result = await db.execute(
            select(Book)
            .where(
                or_(
                    Book.title.ilike(search_term),
                    Book.author.ilike(search_term)
                )
            )
            .order_by(Book.confidence_score.desc().nullslast())
            .limit(limit)
        )
        
        books = result.scalars().all()
        
        return [
            BookResponse(
                id=str(book.id),
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                isbn13=book.isbn13,
                description=book.description,
                publication_year=book.publication_year,
                publisher=book.publisher,
                language=book.language,
                page_count=book.page_count,
                genre=book.genre,
                categories=book.categories,
                tags=book.tags,
                average_rating=book.average_rating,
                ratings_count=book.ratings_count,
                cover_url=book.cover_url,
                amazon_url=book.amazon_url,
                goodreads_url=book.goodreads_url,
                confidence_score=book.confidence_score
            ) for book in books
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching books: {str(e)}")


@router.get("/{book_id}", response_model=BookResponse)
@limiter.limit("60/minute")
async def get_book(
    request: Request,
    book_id: str,
    db: AsyncSession = Depends(get_database)
):
    """Get book details by ID"""
    try:
        result = await db.execute(select(Book).where(Book.id == book_id))
        book = result.scalar_one_or_none()
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return BookResponse(
            id=str(book.id),
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            isbn13=book.isbn13,
            description=book.description,
            publication_year=book.publication_year,
            publisher=book.publisher,
            language=book.language,
            page_count=book.page_count,
            genre=book.genre,
            categories=book.categories,
            tags=book.tags,
            average_rating=book.average_rating,
            ratings_count=book.ratings_count,
            cover_url=book.cover_url,
            amazon_url=book.amazon_url,
            goodreads_url=book.goodreads_url,
            confidence_score=book.confidence_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving book: {str(e)}")


@router.get("/", response_model=List[BookResponse])
@limiter.limit("30/minute")
async def list_books(
    request: Request,
    limit: int = Query(20, le=100, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    genre: Optional[str] = Query(None, description="Filter by genre"),
    author: Optional[str] = Query(None, description="Filter by author"),
    db: AsyncSession = Depends(get_database)
):
    """List books with optional filters"""
    try:
        query = select(Book)
        
        # Apply filters
        if genre:
            query = query.where(Book.genre.ilike(f"%{genre}%"))
        
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))
        
        # Order by confidence score and apply pagination
        query = query.order_by(Book.confidence_score.desc().nullslast())
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        books = result.scalars().all()
        
        return [
            BookResponse(
                id=str(book.id),
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                isbn13=book.isbn13,
                description=book.description,
                publication_year=book.publication_year,
                publisher=book.publisher,
                language=book.language,
                page_count=book.page_count,
                genre=book.genre,
                categories=book.categories,
                tags=book.tags,
                average_rating=book.average_rating,
                ratings_count=book.ratings_count,
                cover_url=book.cover_url,
                amazon_url=book.amazon_url,
                goodreads_url=book.goodreads_url,
                confidence_score=book.confidence_score
            ) for book in books
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing books: {str(e)}")


@router.get("/genres/popular")
@limiter.limit("30/minute")
async def get_popular_genres(
    request: Request,
    limit: int = Query(20, le=50, description="Maximum genres to return"),
    db: AsyncSession = Depends(get_database)
):
    """Get list of popular genres from the book database"""
    try:
        # Get distinct genres, excluding null values
        from sqlalchemy import func, desc
        
        result = await db.execute(
            select(Book.genre, func.count(Book.id).label('book_count'))
            .where(Book.genre.isnot(None))
            .group_by(Book.genre)
            .order_by(desc('book_count'))
            .limit(limit)
        )
        
        genres = result.all()
        
        return {
            "genres": [
                {"name": genre.genre, "book_count": genre.book_count}
                for genre in genres
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving genres: {str(e)}")


@router.get("/authors/popular")
@limiter.limit("30/minute")
async def get_popular_authors(
    request: Request,
    limit: int = Query(20, le=50, description="Maximum authors to return"),
    db: AsyncSession = Depends(get_database)
):
    """Get list of popular authors from the book database"""
    try:
        # Get distinct authors, excluding null values
        from sqlalchemy import func, desc
        
        result = await db.execute(
            select(Book.author, func.count(Book.id).label('book_count'))
            .where(Book.author.isnot(None))
            .group_by(Book.author)
            .order_by(desc('book_count'))
            .limit(limit)
        )
        
        authors = result.all()
        
        return {
            "authors": [
                {"name": author.author, "book_count": author.book_count}
                for author in authors
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving authors: {str(e)}")
