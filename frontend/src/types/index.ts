// User Session Types
export interface UserSession {
  id: string;
  session_id: string;
  device_id?: string;
  name?: string;
  email?: string;
  is_active: boolean;
  created_at: string;
  expires_at: string;
  last_activity: string;
}

export interface CreateSessionRequest {
  device_id?: string;
  user_agent?: string;
  name?: string;
  email?: string;
}

// Book Types
export interface Book {
  id: string;
  title: string;
  author?: string;
  isbn?: string;
  isbn13?: string;
  description?: string;
  publication_year?: number;
  publisher?: string;
  language?: string;
  page_count?: number;
  genre?: string;
  categories?: string[];
  tags?: string[];
  average_rating?: number;
  ratings_count?: number;
  cover_url?: string;
  amazon_url?: string;
  goodreads_url?: string;
  confidence_score?: number;
}

export interface RecognizedBook {
  title: string;
  author?: string;
  confidence: number;
  position?: any;
}

export interface BookRecommendation {
  id: string;
  book: Book;
  reason?: string;
  score?: number;
  source_books?: string[];
  recommendation_type: string;
  is_saved: boolean;
  created_at: string;
}

// User Preferences Types
export interface UserPreferences {
  id: string;
  session_id: string;
  favorite_genres: string[];
  disliked_genres: string[];
  favorite_authors: string[];
  reading_goals: Record<string, any>;
  preferred_length?: string;
  preferred_publication_era?: string;
  content_preferences: Record<string, any>;
  reading_frequency?: string;
  reading_time?: string;
  preferred_format?: string;
  reading_experience?: string;
  language_preferences: string[];
  recommendation_style?: string;
  discovery_openness?: number;
  reading_history: ReadingHistoryItem[];
  created_at: string;
  updated_at: string;
}

export interface ReadingHistoryItem {
  title: string;
  author: string;
  rating?: number;
  date_read?: string;
  review?: string;
}

export interface PreferencesFormData {
  favorite_genres: string[];
  disliked_genres: string[];
  favorite_authors: string[];
  preferred_length?: string;
  preferred_publication_era?: string;
  reading_frequency?: string;
  reading_time?: string;
  preferred_format?: string;
  reading_experience?: string;
  recommendation_style?: string;
  discovery_openness?: number;
}

// Shelf Scan Types
export interface ShelfScanRequest {
  session_id: string;
  use_fallback: boolean;
  max_books: number;
}

export interface ShelfScanResponse {
  scan_id: string;
  recognized_books: RecognizedBook[];
  total_books_found: number;
  processing_time: number;
  api_used: string;
  success: boolean;
  error_message?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// UI State Types
export interface AppState {
  session?: UserSession;
  preferences?: UserPreferences;
  recommendations: BookRecommendation[];
  isLoading: boolean;
  error?: string;
}

// Form Types
export interface ContactFormData {
  name: string;
  email: string;
  message: string;
}

// Common Types
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface SelectOption {
  value: string;
  label: string;
}

// Genre options
export const GENRE_OPTIONS: SelectOption[] = [
  { value: 'fiction', label: 'Fiction' },
  { value: 'non-fiction', label: 'Non-Fiction' },
  { value: 'mystery', label: 'Mystery' },
  { value: 'thriller', label: 'Thriller' },
  { value: 'romance', label: 'Romance' },
  { value: 'sci-fi', label: 'Science Fiction' },
  { value: 'fantasy', label: 'Fantasy' },
  { value: 'biography', label: 'Biography' },
  { value: 'memoir', label: 'Memoir' },
  { value: 'history', label: 'History' },
  { value: 'self-help', label: 'Self-Help' },
  { value: 'business', label: 'Business' },
  { value: 'health', label: 'Health & Wellness' },
  { value: 'cooking', label: 'Cooking' },
  { value: 'travel', label: 'Travel' },
  { value: 'poetry', label: 'Poetry' },
  { value: 'drama', label: 'Drama' },
  { value: 'humor', label: 'Humor' },
  { value: 'children', label: "Children's Books" },
  { value: 'young-adult', label: 'Young Adult' }
];

// Reading experience options
export const READING_EXPERIENCE_OPTIONS: SelectOption[] = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' },
  { value: 'expert', label: 'Expert' }
];

// Book length options
export const BOOK_LENGTH_OPTIONS: SelectOption[] = [
  { value: 'short', label: 'Short (< 200 pages)' },
  { value: 'medium', label: 'Medium (200-400 pages)' },
  { value: 'long', label: 'Long (400+ pages)' },
  { value: 'any', label: 'Any length' }
];

// Reading frequency options
export const READING_FREQUENCY_OPTIONS: SelectOption[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'occasional', label: 'Occasional' }
];
