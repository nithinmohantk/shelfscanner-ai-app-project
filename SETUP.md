# ShelfScanner - Quick Setup Guide

## Prerequisites

- **Docker & Docker Compose** (recommended for easiest setup)
- **Git** for version control
- **OpenAI API Key** (required for book recognition)
- **Node.js 18+** and **Python 3.11+** (for local development)

## 🚀 Quick Start (Docker)

1. **Clone the repository**
   ```bash
   git clone https://github.com/nithinmohantk/shelfscanner-ai-app-project.git
   cd shelfscanner-ai-app-project
   ```

2. **Setup environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🛠️ Local Development Setup

### Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Database Setup (for local development)
```bash
# Start only PostgreSQL and Redis
docker-compose up db redis -d
```

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest --cov=app tests/ --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --build
```

## 🏗️ GitHub Flow Development

1. **Create feature branch from develop**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

3. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a PR to `develop` branch on GitHub.

4. **After PR approval and merge, clean up**
   ```bash
   git checkout develop
   git pull origin develop
   git branch -d feature/your-feature-name
   ```

## 📦 Environment Variables

### Required
- `OPENAI_API_KEY` - Your OpenAI API key for book recognition

### Optional
- `GOOGLE_CLOUD_PROJECT` - Google Cloud project for Vision API fallback
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google service account JSON

### Development Defaults
- Database: PostgreSQL (Docker: postgres/postgres@localhost:5432)
- Redis: localhost:6379
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

## 🐳 Docker Services

- **frontend** - React app (port 3000)
- **backend** - FastAPI app (port 8000)
- **db** - PostgreSQL database (port 5432)
- **redis** - Redis cache (port 6379)

## 🔧 Useful Commands

### Docker
```bash
# Start all services
docker-compose up --build

# Start specific service
docker-compose up backend

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Git Workflow
```bash
# Check current branch
git branch

# Switch branches
git checkout develop
git checkout main

# View commit history
git log --oneline

# View remote branches
git branch -r
```

## 📚 API Usage Examples

### Create Session
```bash
curl -X POST "http://localhost:8000/api/v1/sessions" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe"}'
```

### Scan Bookshelf
```bash
curl -X POST "http://localhost:8000/api/v1/scan/shelf" \
  -F "session_id=your_session_id" \
  -F "image=@bookshelf.jpg" \
  -F "max_books=10"
```

### Get Recommendations
```bash
curl "http://localhost:8000/api/v1/recommend/your_session_id"
```

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in `docker-compose.yml`
2. **OpenAI API errors**: Verify your API key in `.env`
3. **Database connection**: Ensure PostgreSQL is running
4. **Permission denied**: Check Docker permissions on your system

### Debug Commands
```bash
# Check Docker containers
docker ps

# Check container logs
docker logs shelfscanner-backend

# Access container shell
docker exec -it shelfscanner-backend /bin/bash

# Check network connectivity
docker network ls
```

## 🎯 Next Steps

1. Add your OpenAI API key
2. Test the health endpoints
3. Try scanning a bookshelf image
4. Set up your reading preferences
5. Get personalized recommendations!

For detailed development guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
