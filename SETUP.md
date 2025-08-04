# TSX Assessment Book API

A FastAPI-based REST API for managing books with comprehensive testing and CI/CD pipeline.

## Features

- **RESTful API**: Complete CRUD operations for books
- **Comprehensive Testing**: Unit tests with 80%+ coverage requirement
- **CI/CD Pipeline**: Automated testing, linting, and security checks
- **Docker Support**: Containerized development and production environments
- **Code Quality**: Automated formatting, linting, and type checking
- **Security**: Automated security vulnerability scanning

## Quick Start

### Prerequisites

- Python 3.9+
- pip
- Docker (optional)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd tsx-assessment-book
   ```

2. **Install dependencies**
   ```bash
   # Install production dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (recommended)
   pip install -r requirements-dev.txt
   ```

3. **Run the application**
   ```bash
   # Using Python directly
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Using Makefile
   make run
   
   # Using Docker
   docker-compose up app
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Testing

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

# Run tests in parallel
pytest tests/ -n auto

# Using Makefile
make test
make test-cov
make test-fast
```

### Test Coverage

The project requires 80%+ test coverage. Coverage reports are generated in:
- Terminal output
- HTML report: `htmlcov/index.html`
- XML report: `coverage.xml`

### Test Structure

- **Unit Tests**: `tests/test_books.py`
- **Test Configuration**: `tests/conftest.py`
- **Coverage Configuration**: `.coveragerc`

## CI/CD Pipeline

### GitHub Actions Workflow

The CI/CD pipeline (`.github/workflows/ci.yml`) includes:

1. **Testing Job**
   - Runs on Python 3.9, 3.10, 3.11
   - Executes all tests with coverage
   - Generates test reports
   - Uploads coverage to Codecov

2. **Linting Job**
   - Code formatting (Black)
   - Import sorting (isort)
   - Style checking (flake8)
   - Type checking (mypy)

3. **Security Job**
   - Security vulnerability scanning (bandit)
   - Dependency vulnerability checking (safety)

4. **Build Job**
   - Runs only on main branch pushes
   - Prepares for deployment

### Local CI Testing

Test the CI pipeline locally:

```bash
# Run all CI checks locally
make ci-test

# Using Docker
docker-compose --profile test run test
docker-compose --profile lint run lint
docker-compose --profile security run security
```

## Code Quality

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Formatting

```bash
# Format code
black app/ tests/
isort app/ tests/

# Using Makefile
make format
```

### Linting

```bash
# Run linting checks
flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203,W503
black --check --diff app/ tests/
isort --check-only --diff app/ tests/
mypy app/ --ignore-missing-imports

# Using Makefile
make lint
```

## Docker

### Development

```bash
# Build and run development container
docker-compose up app

# Build and run with hot reload
docker-compose up app
```

### Production

```bash
# Build production image
docker build --target production -t tsx-assessment-book .

# Run production container
docker run -p 8000:8000 tsx-assessment-book

# Using docker-compose
docker-compose --profile production up app-prod
```

### Testing with Docker

```bash
# Run tests in container
docker-compose --profile test run test

# Run linting in container
docker-compose --profile lint run lint

# Run security checks in container
docker-compose --profile security run security
```

## API Endpoints

### Books

- `POST /create-book` - Create a new book
- `GET /get-books` - List all books (with optional tag filtering)
- `GET /get-books/{book_id}` - Get a specific book
- `PUT /books/{book_id}` - Update a book
- `DELETE /books/{book_id}` - Delete a book

### Utility

- `GET /` - Health check
- `GET /random-number` - Get random numbers
- `GET /random-number-sum` - Get sum of random numbers

### Documentation

- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `GET /openapi.json` - OpenAPI schema

## Development Commands

### Makefile Commands

```bash
make help          # Show all available commands
make install       # Install production dependencies
make install-dev   # Install development dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make test-fast     # Run tests in parallel
make lint          # Run linting checks
make format        # Format code
make security      # Run security checks
make clean         # Clean generated files
make run           # Run development server
make run-prod      # Run production server
make ci-test       # Run all CI checks locally
```

### Docker Commands

```bash
# Development
docker-compose up app

# Testing
docker-compose --profile test run test

# Linting
docker-compose --profile lint run lint

# Security
docker-compose --profile security run security

# Production
docker-compose --profile production up app-prod
```

## Project Structure

```
tsx-assessment-book/
├── .github/workflows/     # GitHub Actions CI/CD
├── app/                   # Application code
│   ├── api/routes/       # API endpoints
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   └── utils/            # Utilities
├── tests/                # Test files
├── logs/                 # Application logs
├── .coveragerc          # Coverage configuration
├── .gitignore           # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks
├── docker-compose.yml   # Docker Compose configuration
├── Dockerfile           # Docker configuration
├── Makefile             # Development commands
├── pytest.ini          # Pytest configuration
├── requirements.txt     # Production dependencies
├── requirements-dev.txt # Development dependencies
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `make ci-test`
5. Commit your changes: `git commit -m "Add feature"`
6. Push to your branch: `git push origin feature-branch`
7. Create a Pull Request

### Development Workflow

1. **Setup**: `make install-dev`
2. **Develop**: Make changes to code
3. **Test**: `make test-cov`
4. **Format**: `make format`
5. **Lint**: `make lint`
6. **Commit**: Changes will be automatically checked by pre-commit hooks

## Monitoring and Logging

- Application logs are stored in `logs/`
- Test reports are generated in `reports/`
- Coverage reports are in `htmlcov/`

## Security

- Automated security scanning with bandit
- Dependency vulnerability checking with safety
- Non-root Docker containers
- Health checks for containers

## Performance

- Parallel test execution support
- Docker layer caching
- Optimized production Docker image
- Gunicorn with multiple workers in production

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `PYTHONPATH` is set correctly
2. **Test failures**: Check that all dependencies are installed
3. **Docker issues**: Ensure Docker is running and ports are available
4. **Coverage issues**: Check `.coveragerc` configuration

### Getting Help

- Check the test output for detailed error messages
- Review the CI/CD logs in GitHub Actions
- Ensure all dependencies are properly installed
- Verify Docker containers are running correctly

## License

[Add your license information here]