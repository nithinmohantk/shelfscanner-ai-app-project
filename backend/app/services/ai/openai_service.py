"""
OpenAI GPT-4 Vision Service for Book Recognition
"""

import base64
import asyncio
from typing import List, Dict, Any
from openai import AsyncOpenAI
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIVisionService:
    """Service for book recognition using OpenAI GPT-4 Vision API"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image: {e}")
            raise
    
    async def identify_books(self, image_path: str, max_books: int = 20) -> List[Dict[str, Any]]:
        """
        Identify books from shelf image using GPT-4 Vision
        
        Args:
            image_path: Path to the uploaded image
            max_books: Maximum number of books to identify
            
        Returns:
            List of identified books with metadata
        """
        try:
            # Encode image
            base64_image = self.encode_image(image_path)
            
            # Create prompt for book identification
            prompt = f"""
            You are an expert librarian and book identifier. Analyze this bookshelf image and identify up to {max_books} books.
            
            For each book you can clearly identify, provide:
            1. Title (exact as shown on spine)
            2. Author (if visible)
            3. Confidence level (0.0 to 1.0) - how certain you are about the identification
            4. Position description (e.g., "top shelf, left side")
            
            Rules:
            - Only identify books where you can clearly read the title
            - Don't guess or make up titles
            - If you can only see part of a title, indicate with "..." 
            - Provide confidence scores honestly - lower scores for unclear text
            - Focus on the most legible books first
            
            Return your response as a JSON array with this format:
            [
                {{
                    "title": "Book Title",
                    "author": "Author Name" or null,
                    "confidence": 0.95,
                    "position": "description of location on shelf"
                }}
            ]
            
            Important: Return ONLY the JSON array, no other text.
            """
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse response
            content = response.choices[0].message.content
            logger.info(f"OpenAI response: {content}")
            
            # Try to parse JSON response
            import json
            try:
                books = json.loads(content)
                if not isinstance(books, list):
                    logger.error("OpenAI response is not a list")
                    return []
                
                # Validate and clean up the response
                validated_books = []
                for book in books[:max_books]:
                    if isinstance(book, dict) and "title" in book:
                        validated_book = {
                            "title": str(book["title"]).strip(),
                            "author": str(book.get("author", "")).strip() if book.get("author") else None,
                            "confidence": float(book.get("confidence", 0.5)),
                            "position": str(book.get("position", "")).strip() if book.get("position") else None
                        }
                        
                        # Skip empty titles
                        if validated_book["title"]:
                            validated_books.append(validated_book)
                
                logger.info(f"Successfully identified {len(validated_books)} books")
                return validated_books
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI JSON response: {e}")
                logger.error(f"Raw response: {content}")
                return []
                
        except Exception as e:
            logger.error(f"OpenAI Vision API error: {e}")
            raise
    
    async def get_book_recommendations(
        self, 
        user_preferences: Dict[str, Any], 
        recognized_books: List[Dict[str, Any]],
        max_recommendations: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Generate book recommendations based on user preferences and recognized books
        """
        try:
            # Prepare context
            prefs_text = self._format_preferences(user_preferences)
            books_text = self._format_recognized_books(recognized_books)
            
            prompt = f"""
            You are an expert book recommender. Based on the user's reading preferences and the books they've encountered on a shelf, recommend {max_recommendations} books they might enjoy.
            
            User's Reading Preferences:
            {prefs_text}
            
            Books Found on Shelf:
            {books_text}
            
            Provide personalized recommendations that:
            1. Align with their stated preferences
            2. Consider books similar to what they found interesting
            3. Include a mix of popular and lesser-known titles
            4. Respect any dislikes or content preferences
            
            For each recommendation, provide:
            - Title and Author
            - Brief reason why it matches their preferences
            - Similarity to shelf books (if applicable)
            - Estimated appeal score (0.0-1.0)
            
            Return as JSON array:
            [
                {{
                    "title": "Book Title",
                    "author": "Author Name",
                    "reason": "Why this book matches their preferences",
                    "similarity_to": "Title of similar shelf book or null",
                    "appeal_score": 0.85,
                    "genre": "Primary genre",
                    "publication_year": 2020 or null
                }}
            ]
            
            Return ONLY the JSON array.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo",  # Use text model for recommendations
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            import json
            try:
                recommendations = json.loads(content)
                return recommendations[:max_recommendations]
            except json.JSONDecodeError:
                logger.error(f"Failed to parse recommendations JSON: {content}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise
    
    def _format_preferences(self, preferences: Dict[str, Any]) -> str:
        """Format user preferences for prompt"""
        lines = []
        
        if preferences.get("favorite_genres"):
            lines.append(f"Favorite genres: {', '.join(preferences['favorite_genres'])}")
        
        if preferences.get("disliked_genres"):
            lines.append(f"Dislikes: {', '.join(preferences['disliked_genres'])}")
            
        if preferences.get("favorite_authors"):
            lines.append(f"Favorite authors: {', '.join(preferences['favorite_authors'])}")
            
        if preferences.get("reading_experience"):
            lines.append(f"Reading level: {preferences['reading_experience']}")
            
        if preferences.get("preferred_length"):
            lines.append(f"Preferred book length: {preferences['preferred_length']}")
            
        return "\n".join(lines) if lines else "No specific preferences provided"
    
    def _format_recognized_books(self, books: List[Dict[str, Any]]) -> str:
        """Format recognized books for prompt"""
        if not books:
            return "No books were clearly identified from the shelf image"
        
        lines = []
        for book in books:
            title = book.get("title", "Unknown")
            author = book.get("author", "Unknown author")
            confidence = book.get("confidence", 0.0)
            lines.append(f"- {title} by {author} (confidence: {confidence:.1f})")
        
        return "\n".join(lines)
