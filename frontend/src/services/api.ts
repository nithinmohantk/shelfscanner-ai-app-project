import axios from 'axios';
import type {
  UserSession,
  CreateSessionRequest,
  UserPreferences,
  PreferencesFormData,
  BookRecommendation,
  ShelfScanResponse,
  Book
} from '../types';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding session info
api.interceptors.request.use((config) => {
  // You can add session handling here if needed
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Session API
export const sessionAPI = {
  async createSession(data: CreateSessionRequest): Promise<UserSession> {
    const response = await api.post<UserSession>('/sessions', data);
    return response.data;
  },

  async getSession(sessionId: string): Promise<UserSession> {
    const response = await api.get<UserSession>(`/sessions/${sessionId}`);
    return response.data;
  },

  async updateSession(sessionId: string, data: Partial<CreateSessionRequest>): Promise<UserSession> {
    const response = await api.put<UserSession>(`/sessions/${sessionId}`, data);
    return response.data;
  },

  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/sessions/${sessionId}`);
  },
};

// Preferences API
export const preferencesAPI = {
  async createPreferences(data: PreferencesFormData & { session_id: string }): Promise<UserPreferences> {
    const response = await api.post<UserPreferences>('/preferences', data);
    return response.data;
  },

  async getPreferences(sessionId: string): Promise<UserPreferences> {
    const response = await api.get<UserPreferences>(`/preferences/${sessionId}`);
    return response.data;
  },

  async updatePreferences(sessionId: string, data: PreferencesFormData): Promise<UserPreferences> {
    const response = await api.put<UserPreferences>(`/preferences/${sessionId}`, data);
    return response.data;
  },

  async importGoodreads(data: {
    session_id: string;
    goodreads_user_id?: string;
    goodreads_data: any;
    merge_with_existing: boolean;
  }): Promise<{ message: string; books_imported: number }> {
    const response = await api.post('/preferences/import-goodreads', data);
    return response.data;
  },
};

// Scan API
export const scanAPI = {
  async scanShelf(
    sessionId: string,
    imageFile: File,
    options: {
      use_fallback?: boolean;
      max_books?: number;
    } = {}
  ): Promise<ShelfScanResponse> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('image', imageFile);
    formData.append('use_fallback', String(options.use_fallback ?? true));
    formData.append('max_books', String(options.max_books ?? 20));

    const response = await api.post<ShelfScanResponse>('/scan/shelf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for image processing
    });
    
    return response.data;
  },

  async getScanHistory(sessionId: string, limit: number = 10): Promise<any[]> {
    const response = await api.get(`/scan/history/${sessionId}`, {
      params: { limit }
    });
    return response.data.scans || [];
  },

  async cleanupScan(scanId: string): Promise<void> {
    await api.delete(`/scan/cleanup/${scanId}`);
  },
};

// Recommendations API
export const recommendationsAPI = {
  async generateRecommendations(data: {
    session_id: string;
    shelf_scan_id?: string;
    max_recommendations?: number;
    include_similar?: boolean;
    include_new?: boolean;
  }): Promise<BookRecommendation[]> {
    const response = await api.post<BookRecommendation[]>('/recommend/generate', data);
    return response.data;
  },

  async getRecommendations(sessionId: string, limit: number = 20): Promise<BookRecommendation[]> {
    const response = await api.get<BookRecommendation[]>(`/recommend/${sessionId}`, {
      params: { limit }
    });
    return response.data;
  },

  async trackInteraction(data: {
    recommendation_id: string;
    interaction_type: 'viewed' | 'saved' | 'interested' | 'purchased';
    additional_data?: any;
  }): Promise<void> {
    await api.post('/recommend/interaction', data);
  },
};

// Books API
export const booksAPI = {
  async searchBooks(query: string, limit: number = 20): Promise<Book[]> {
    const response = await api.get<Book[]>('/books/search', {
      params: { q: query, limit }
    });
    return response.data;
  },

  async getBook(bookId: string): Promise<Book> {
    const response = await api.get<Book>(`/books/${bookId}`);
    return response.data;
  },

  async listBooks(params: {
    limit?: number;
    offset?: number;
    genre?: string;
    author?: string;
  } = {}): Promise<Book[]> {
    const response = await api.get<Book[]>('/books', { params });
    return response.data;
  },

  async getPopularGenres(limit: number = 20): Promise<{ name: string; book_count: number }[]> {
    const response = await api.get(`/books/genres/popular`, {
      params: { limit }
    });
    return response.data.genres;
  },

  async getPopularAuthors(limit: number = 20): Promise<{ name: string; book_count: number }[]> {
    const response = await api.get(`/books/authors/popular`, {
      params: { limit }
    });
    return response.data.authors;
  },
};

// Health check
export const healthAPI = {
  async checkHealth(): Promise<{ status: string; environment: string; version: string }> {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
