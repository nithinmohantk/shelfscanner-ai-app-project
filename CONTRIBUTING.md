# Contributing to ShelfScanner

We welcome contributions to the ShelfScanner AI book discovery app! This document outlines our development workflow and guidelines.

## GitHub Flow

We follow the **GitHub Flow** branching strategy for development:

### Branch Structure

- **`main`** - Production-ready code, always deployable
- **`develop`** - Integration branch for ongoing development
- **`feature/*`** - Feature development branches
- **`hotfix/*`** - Emergency fixes for production issues
- **`release/*`** - Release preparation branches

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add book recommendation algorithm"
   ```

4. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   - Create a Pull Request to the `develop` branch
   - Provide a clear description of changes
   - Link any relevant issues

5. **Code Review Process**
   - At least one reviewer approval required
   - All CI/CD checks must pass
   - Address any feedback promptly

6. **Merge to Develop**
   - Use "Squash and Merge" for feature branches
   - Delete the feature branch after merging

7. **Release Process**
   - Create `release/v1.x.x` branch from `develop`
   - Final testing and bug fixes
   - Merge to `main` and tag the release
   - Merge back to `develop`

## Commit Message Convention

We use [Conventional Commits](https://conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples
```
feat(backend): add OpenAI vision integration
fix(frontend): resolve image upload validation issue
docs: update API documentation
test(backend): add integration tests for recommendations
```

## Code Quality Standards

### Backend (Python/FastAPI)
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for modules, classes, and functions
- Maintain test coverage above 80%
- Use async/await for all database operations

### Frontend (React/TypeScript)
- Use TypeScript for all components
- Follow React best practices and hooks patterns
- Use Tailwind CSS for styling
- Write component tests with Jest/React Testing Library
- Maintain responsive design principles

### General
- No hardcoded credentials or secrets
- Use environment variables for configuration
- Write meaningful variable and function names
- Keep functions small and focused
- Add comments for complex logic

## Testing Requirements

### Backend Testing
```bash
cd backend
pytest --cov=app tests/ --cov-report=html
```

### Frontend Testing
```bash
cd frontend
npm test -- --coverage --watchAll=false
```

### Integration Testing
```bash
docker-compose -f docker-compose.test.yml up --build
```

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/nithinmohantk/shelfscanner-ai-app-project.git
   cd shelfscanner-ai-app-project
   ```

2. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Local Development Setup**
   
   **Backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
   
   **Frontend:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Pull Request Guidelines

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added/updated and passing
- [ ] Documentation updated if needed
- [ ] No merge conflicts with target branch

### PR Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

## Issue Reporting

When reporting bugs or requesting features:

1. Use the appropriate issue template
2. Provide clear reproduction steps
3. Include environment details
4. Add relevant labels
5. Reference related issues/PRs

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers get started
- Follow project guidelines
- Keep discussions focused and professional

## Getting Help

- Check existing documentation first
- Search issues for similar problems
- Join discussions in issue comments
- Tag maintainers if urgent

## Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor insights

Thank you for contributing to ShelfScanner! 🚀📚
