# ShelfScanner AI Book Discovery App

An AI-powered book discovery application that helps users identify unknown books on shelves and provides personalized reading recommendations using OpenAI GPT-4 Vision API.

## 🚀 Features

- **Book Recognition**: Upload photos of bookshelves to identify books using AI
- **Personalized Recommendations**: Get tailored book suggestions based on your reading preferences
- **Reading History Integration**: Import your Goodreads data for better recommendations
- **Mobile-Friendly**: Responsive web app optimized for mobile devices
- **No Account Required**: Device-based session management for simplicity

## 🏗️ Architecture

- **Backend**: Python FastAPI with PostgreSQL database
- **Frontend**: React with Vite for fast development
- **AI Services**: OpenAI GPT-4 Vision API with Google Vision API fallback
- **Infrastructure**: Docker containers with GitHub Actions CI/CD
- **Caching**: Redis for book metadata and API response caching

## 🛠️ Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Frontend**: React, Vite, TypeScript, Tailwind CSS
- **AI/ML**: OpenAI GPT-4 Vision API, Google Vision API
- **DevOps**: Docker, Docker Compose, GitHub Actions
- **Deployment**: Containerized deployment ready for cloud platforms

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Environment Variables

Create a `.env` file in the root directory:

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Google Cloud (optional fallback)
GOOGLE_CLOUD_PROJECT=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Database
POSTGRES_DB=shelfscanner
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_db_password
DATABASE_URL=postgresql://postgres:your_db_password@db:5432/shelfscanner

# Redis
REDIS_URL=redis://redis:6379

# App Configuration
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ENVIRONMENT=development
```

### Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📱 Usage

1. **Set Preferences**: Input your reading preferences and genres you enjoy
2. **Upload Goodreads Data**: (Optional) Import your reading history
3. **Scan Bookshelf**: Take a photo of any bookshelf
4. **Get Recommendations**: Receive personalized book suggestions
5. **Save or Buy**: Save books for later or purchase directly from Amazon

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose -f docker-compose.test.yml up --build
```

## 📦 Deployment

The project includes GitHub Actions workflows for automated:
- Building and testing
- Publishing Docker images to DockerHub
- Security scanning and code quality checks

## 🔒 Security Features

- Input validation and sanitization
- Rate limiting to prevent abuse
- CORS configuration
- Environment variable management
- SQL injection protection

## 📈 Monitoring

- Health check endpoints
- Basic usage analytics
- Error tracking and logging
- Cost monitoring for AI API usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions, please create an issue in the GitHub repository.
