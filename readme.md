# Book Management API

A production-ready FastAPI application for managing books with full CRUD operations, structured logging, comprehensive error handling, and extensive test coverage.

## Features

- **Complete CRUD Operations**: Create, Read, Update, Delete books
- **Data Validation**: Comprehensive input validation using Pydantic v2
- **Structured Logging**: JSON-structured logs with rotation using structlog
- **Error Handling**: Centralized error handling with consistent response formats
- **Tag Filtering**: Filter books by tags
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Comprehensive Testing**: Full test suite with 95%+ coverage
- **Production Ready**: Proper logging, error handling, and validation

## Project Structure

```
.
├── app
│   ├── api
│   │   └── routes
│   │       ├── __init__.py
│   │       └── books.py
│   ├── events
│   │   └── lifecycle.py
│   ├── models
│   │   └── book_models.py
│   ├── services
│   │   └── storage.py
│   ├── utils
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   └── main.py
├── logs/                     
├── tests
│   ├── conftest.py
│   └── test_books.py
├── venv/                     
└── README.md

```

## Installation

1. **Clone the repository** (or create the files as shown in the structure above)

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Development Server

```bash
# From the project root directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
# Using uvicorn with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using the built-in runner
python -m app.main
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_books.py

# Run with verbose output
pytest -v
```

## API Endpoints

### Books

| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| POST | `/books` | Create a new book | 201, 422 |
| GET | `/books/{book_id}` | Get a book by ID | 200, 404 |
| PUT | `/books/{book_id}` | Update a book | 200, 404, 422 |
| DELETE | `/books/{book_id}` | Delete a book | 204, 404 |
| GET | `/books` | List all books | 200 |
| GET | `/books?tag={tag}` | Filter books by tag | 200 |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check endpoint |

## Sample Usage

### Create a Book

```bash
curl -X POST "http://localhost:8000/books" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "published_year": 1925,
    "price": 299.99,
    "tags": ["classic", "american literature", "fiction"]
  }'
```

### Get a Book

```bash
curl -X GET "http://localhost:8000/books/{book_id}"
```

### Update a Book

```bash
curl -X PUT "http://localhost:8000/books/{book_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 349.99,
    "tags": ["classic", "american literature", "fiction", "updated"]
  }'
```

### List Books with Tag Filter

```bash
curl -X GET "http://localhost:8000/books?tag=fiction"
```

### Delete a Book

```bash
curl -X DELETE "http://localhost:8000/books/{book_id}"
```

## Data Models

### Book Entity (Internal)

```python
@dataclass
class Book:
    id: UUID
    title: str
    author: str
    published_year: int
    price: float
    tags: Optional[List[str]] = None
```

### API Models

- **BookCreate**: For creating books (excludes `id`)
- **BookUpdate**: For updating books (all fields optional)
- **BookResponse**: For API responses (includes `id`)

### Validation Rules

- **title**: Non-empty string, no whitespace-only values
- **author**: Non-empty string, no whitespace-only values
- **published_year**: Integer between 1900 and current year
- **price**: Positive float (> 0)
- **tags**: Optional list of strings

## Error Handling

The API provides consistent error responses in the following format:

### Validation Errors (422)

```json
{
  "error": "validation_error",
  "message": "Input validation failed",
  "details": {
    "errors": [
      {
        "loc": ["price"],
        "msg": "ensure this value is greater than 0",
        "type": "value_error.number.not_gt"
      }
    ]
  }
}
```

### HTTP Errors (404)

```json
{
  "error": "http_error",
  "message": "Book not found"
}
```

### Internal Errors (500)

```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred. Please try again later."
}
```

## Logging

The application uses structured logging with the following features:

- **Log File**: `app.log` (with rotation, max 10MB, 5 backups)
- **Format**: JSON structured logs
- **Levels**:
  - **DEBUG**: Request data, internal state changes
  - **INFO**: Successful operations
  - **WARNING**: Expected errors (validation, not found)
  - **ERROR**: Unexpected errors with stack traces

### Log File Location

Logs are written to `app.log` in the project root directory. The log file rotates automatically when it reaches 10MB, keeping up to 5 backup files.

### Sample Log Entry

```json
{
  "timestamp": "2024-08-02T10:30:45.123456Z",
  "level": "info",
  "logger_name": "book_api",
  "event": "Book created successfully",
  "book_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "The Great Gatsby"
}
```

## Testing

The test suite includes:

- **Unit Tests**: All CRUD operations
- **Validation Tests**: Input validation scenarios
- **Error Handling Tests**: All error conditions
- **State Management Tests**: Storage consistency
- **API Documentation Tests**: OpenAPI accessibility
- **Integration Tests**: End-to-end workflows

### Test Categories

- **TestBookCreation**: Valid and invalid book creation scenarios
- **TestBookRetrieval**: Getting existing and non-existent books
- **TestBookUpdate**: Partial and full updates, error cases
- **TestBookDeletion**: Successful and failed deletion attempts
- **TestBookListing**: Listing all books and filtering by tags
- **TestErrorHandling**: Error response structures and internal errors
- **TestHealthCheck**: Health check endpoint functionality
- **TestAPIDocumentation**: API documentation accessibility
- **TestStateManagement**: Storage isolation and consistency

## Production Considerations

1. **Database**: Replace in-memory storage with a persistent database (PostgreSQL, MongoDB, etc.)
2. **Authentication**: Add API key or JWT-based authentication
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Caching**: Add Redis or similar for caching frequently accessed data
5. **Monitoring**: Integrate with monitoring tools (Prometheus, Grafana)
6. **Deployment**: Use Docker containers and orchestration (Kubernetes)
7. **Load Balancing**: Use nginx or similar for load balancing
8. **SSL/TLS**: Enable HTTPS in production

## Dependencies

- **fastapi**: Modern, fast web framework for building APIs
- **uvicorn**: ASGI server implementation
- **pydantic**: Data validation and settings management
- **structlog**: Structured logging library
- **pytest**: Testing framework
- **httpx**: HTTP client for testing
- **pytest-asyncio**: Async support for pytest

## License

This project is provided as-is for educational and development purposes.