"""
Google Cloud Vision Service for Book Recognition (Fallback)
"""

import asyncio
from typing import List, Dict, Any
import logging
import re

try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    vision = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleVisionService:
    """Service for book recognition using Google Cloud Vision API as fallback"""
    
    def __init__(self):
        if not GOOGLE_VISION_AVAILABLE:
            raise ImportError("google-cloud-vision package not installed")
        
        if not settings.GOOGLE_CLOUD_PROJECT:
            raise ValueError("Google Cloud project not configured")
        
        self.client = vision.ImageAnnotatorClient()
    
    async def identify_books(self, image_path: str, max_books: int = 20) -> List[Dict[str, Any]]:
        """
        Identify books from shelf image using Google Vision OCR
        
        Args:
            image_path: Path to the uploaded image
            max_books: Maximum number of books to identify
            
        Returns:
            List of identified books with metadata
        """
        try:
            # Run OCR detection in a separate thread to make it async
            loop = asyncio.get_event_loop()
            texts = await loop.run_in_executor(None, self._detect_text, image_path)
            
            # Process detected text to find book titles
            books = self._extract_books_from_text(texts, max_books)
            
            logger.info(f"Google Vision identified {len(books)} potential books")
            return books
            
        except Exception as e:
            logger.error(f"Google Vision API error: {e}")
            raise
    
    def _detect_text(self, image_path: str) -> List[Dict[str, Any]]:
        """Detect text in image using Google Vision OCR"""
        try:
            # Load image
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            
            # Detect text
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if response.error.message:
                raise Exception(f'Google Vision API error: {response.error.message}')
            
            # Convert to list of dictionaries with text and bounding box info
            detected_texts = []
            for text in texts:
                detected_texts.append({
                    'text': text.description,
                    'bounds': [(vertex.x, vertex.y) for vertex in text.bounding_poly.vertices],
                    'confidence': 1.0  # Google Vision doesn't provide confidence for text detection
                })
            
            return detected_texts
            
        except Exception as e:
            logger.error(f"Error detecting text with Google Vision: {e}")
            raise
    
    def _extract_books_from_text(self, texts: List[Dict[str, Any]], max_books: int) -> List[Dict[str, Any]]:
        """Extract potential book titles from detected text"""
        if not texts:
            return []
        
        # Get the full text (first element is usually the complete text)
        full_text = texts[0]['text'] if texts else ""
        
        # Split into lines and filter for potential book titles
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        books = []
        processed_titles = set()
        
        for line in lines:
            # Skip very short lines (likely not book titles)
            if len(line) < 3:
                continue
            
            # Skip lines that look like numbers, barcodes, or publishing info
            if self._is_likely_metadata(line):
                continue
            
            # Clean up the text
            cleaned_title = self._clean_title(line)
            
            if cleaned_title and cleaned_title.lower() not in processed_titles:
                # Try to separate title and author if possible
                title, author = self._separate_title_author(cleaned_title)
                
                # Estimate confidence based on text characteristics
                confidence = self._estimate_confidence(cleaned_title)
                
                book = {
                    'title': title,
                    'author': author,
                    'confidence': confidence,
                    'position': None  # Google Vision doesn't easily provide position context
                }
                
                books.append(book)
                processed_titles.add(cleaned_title.lower())
                
                if len(books) >= max_books:
                    break
        
        # Sort by confidence
        books.sort(key=lambda x: x['confidence'], reverse=True)
        
        return books[:max_books]
    
    def _is_likely_metadata(self, text: str) -> bool:
        """Check if text looks like metadata rather than a book title"""
        # Common patterns for non-title text
        metadata_patterns = [
            r'^\d+$',  # Just numbers
            r'isbn',   # ISBN references
            r'^\$\d+', # Prices
            r'^\d{4}$', # Years
            r'^[A-Z]{2,4}\d+', # Catalog numbers
            r'barcode', # Barcode text
            r'copyright',
            r'edition',
            r'published',
            r'pages?'
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in metadata_patterns)
    
    def _clean_title(self, text: str) -> str:
        """Clean up detected text to extract likely book title"""
        # Remove common OCR artifacts and cleanup
        cleaned = re.sub(r'[^\w\s\-:.,\'\"()]', ' ', text)
        cleaned = ' '.join(cleaned.split())  # Normalize whitespace
        
        # Remove very common words that are often OCR errors
        noise_words = ['the', 'a', 'an', 'and', 'or', 'but', 'of', 'in', 'on', 'at', 'to', 'for']
        words = cleaned.split()
        
        # Don't clean if it would remove too much
        if len(words) > 2:
            words = [w for w in words if w.lower() not in noise_words or len(w) > 3]
        
        return ' '.join(words)
    
    def _separate_title_author(self, text: str) -> tuple:
        """Try to separate title and author from combined text"""
        # Look for common patterns that separate title and author
        separators = [' by ', ' BY ', ' - ', ' – ', ' | ']
        
        for sep in separators:
            if sep in text:
                parts = text.split(sep, 1)
                return parts[0].strip(), parts[1].strip()
        
        # If no clear separator, assume it's just a title
        return text.strip(), None
    
    def _estimate_confidence(self, text: str) -> float:
        """Estimate confidence in the text being a book title"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for title-like characteristics
        if len(text) > 5:
            confidence += 0.1
        
        if len(text.split()) > 1:  # Multi-word titles are more likely
            confidence += 0.1
        
        if text[0].isupper():  # Capitalized first letter
            confidence += 0.1
        
        if any(word[0].isupper() for word in text.split()[1:]):  # Title case
            confidence += 0.1
        
        # Reduce confidence for suspicious patterns
        if re.search(r'\d{3,}', text):  # Long numbers
            confidence -= 0.2
        
        if len(text) > 100:  # Very long text
            confidence -= 0.2
        
        return max(0.1, min(1.0, confidence))  # Clamp between 0.1 and 1.0
