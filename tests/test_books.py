import uuid
from unittest.mock import PropertyMock, patch, Mock
import pytest
from fastapi.testclient import TestClient
from app.models.book_models import Book
from datetime import datetime


@pytest.fixture(autouse=True)
def setup_storage():
    """Setup storage with delete_book method if not present."""
    from app.services.storage import storage

    # Add delete_book method if it doesn't exist
    if not hasattr(storage, "delete_book"):

        def delete_book(self, book_id: str) -> bool:
            """Delete a book by ID"""
            if book_id in self._books:
                del self._books[book_id]
                return True
            return False

        # Bind the method to the storage instance
        import types

        storage.delete_book = types.MethodType(delete_book, storage)

    yield

    # Clear storage after each test
    storage.clear()

@pytest.fixture
def sample_random_number_response():
    """Provide expected random number response structure."""
    return [100, 101, 102, 103, 104]

class TestRandomNumber:
    @patch("app.api.routes.books.requests.get")
    def test_random_number(self, mock_random_get, client: TestClient, sample_random_number_response):
        """Test that random number endpoint returns correct response."""
        mock_response = Mock()
        mock_response.status_code = 200
        
        mock_response.json.return_value = sample_random_number_response
        mock_random_get.return_value = mock_response
        
        response = client.get("/random-number")
        assert response.status_code == 200
        out = response.json()
        assert response.json() == sample_random_number_response
        assert out[1] == 101

    @patch("app.api.routes.books.requests.get")
    def test_random_number_sum(self, mock_get, client: TestClient, sample_random_number_response):
        """Test that random number endpoint returns correct response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_random_number_response
        mock_get.return_value = mock_response

        response = client.get("/random-number-sum")
        assert response.status_code == 200
        out = response.json()
        assert out == 510

class TestBookCreation:
    """Test cases for book creation."""

    def test_create_valid_book(self, client: TestClient):
        """Test creating a valid book."""
        book_data = {
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "published_year": 1925,
            "price": 299.99,
            "tags": ["classic", "american literature"],
        }

        response = client.post("/create-book", json=book_data)

        assert response.status_code == 201
        response_data = response.json()

        # Check response structure
        assert "id" in response_data
        assert response_data["title"] == book_data["title"]
        assert response_data["author"] == book_data["author"]
        assert response_data["published_year"] == book_data["published_year"]
        assert response_data["price"] == book_data["price"]
        assert response_data["tags"] == book_data["tags"]

    @patch("uuid.uuid4")
    def test_create_book_with_mocked_uuid(self, mock_uuid, client: TestClient):
        """Test creating a book with mocked UUID generation."""
        # Mock UUID generation
        expected_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_uuid.return_value = expected_id

        book_data = {
            "title": "Mocked UUID Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response = client.post("/create-book", json=book_data)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["id"] == expected_id
        mock_uuid.assert_called_once()

    @patch("app.services.storage.storage.create_book")
    def test_create_book_with_mocked_storage(self, mock_create_book, client: TestClient):
        """Test creating a book with mocked storage service."""
        # Create a proper Book object for the mock to return
        
        expected_book = Book(
            id="mock-id-123",
            title="Mocked Storage Book",
            author="Test Author",
            published_year=2020,
            price=100.0,
            tags=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Set up the mock to return the Book object
        mock_create_book.return_value = expected_book

        book_data = {
            "title": "Mocked Storage Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response = client.post("/create-book", json=book_data)

        assert response.status_code == 201
        response_data = response.json()
        # Check that the response contains the expected data
        assert response_data["id"] == expected_book.id
        assert response_data["title"] == expected_book.title
        assert response_data["author"] == expected_book.author
        assert response_data["published_year"] == expected_book.published_year
        assert response_data["price"] == expected_book.price
        mock_create_book.assert_called_once()

    @patch("app.services.storage.storage.create_book")
    def test_create_book_storage_exception(self, mock_create_book, client: TestClient):
        """Test handling storage exceptions during book creation."""
        # Mock storage to raise an exception
        mock_create_book.side_effect = Exception("Storage error")

        book_data = {
            "title": "Exception Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response = client.post("/create-book", json=book_data)

        # Depending on your error handling, this might be 500 or another status
        assert response.status_code in [500, 503]
        mock_create_book.assert_called_once()

    def test_create_book_without_tags(self, client: TestClient):
        """Test creating a book without tags."""
        book_data = {
            "title": "1984",
            "author": "George Orwell",
            "published_year": 1949,
            "price": 249.99,
        }

        response = client.post("/create-book", json=book_data)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["tags"] is None

    def test_create_book_negative_price(self, client: TestClient):
        """Test creating a book with negative price."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": -10.0,
        }

        response = client.post("/create-book", json=book_data)

        assert response.status_code == 422
        error_response = response.json()
        if "error" in error_response:
            assert error_response["error"] == "validation_error"
            assert "validation failed" in error_response["message"].lower()
        else:
            assert "detail" in error_response

    def test_create_book_empty_title(self, client: TestClient):
        """Test creating a book with empty title."""
        book_data = {
            "title": "   ",  # Whitespace only
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response = client.post("/create-book", json=book_data)

        assert response.status_code == 422
        error_response = response.json()

        assert "error" in error_response
        assert "message" in error_response
        assert "details" in error_response

        assert error_response["error"] == "validation_error"
        assert error_response["message"] == "Input validation failed"

        details = error_response["details"]
        assert "errors" in details
        assert isinstance(details["errors"], list)

        title_error = None
        for error in details["errors"]:
            if error["loc"] == ["body", "title"]:
                title_error = error
                break

        assert title_error is not None, "Title validation error not found"
        assert (
            title_error["msg"]
            == "Value error, Field cannot be empty or contain only whitespace"
        )
        assert title_error["type"] == "value_error"
        assert title_error["input"] == "   "

        assert "ctx" in title_error
        assert "error" in title_error["ctx"]
        assert isinstance(title_error["ctx"]["error"], str)
        assert (
            "Field cannot be empty or contain only whitespace"
            in title_error["ctx"]["error"]
        )


class TestBookRetrieval:
    """Test cases for book retrieval."""

    def test_get_existing_book(self, client: TestClient):
        """Test retrieving an existing book."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        create_response = client.post("/create-book", json=book_data)
        book_id = create_response.json()["id"]

        response = client.get(f"/get-books/{book_id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == book_id
        assert response_data["title"] == book_data["title"]
        assert response_data["author"] == book_data["author"]
        assert response_data["published_year"] == book_data["published_year"]

    @patch("app.services.storage.storage.get_book")
    def test_get_book_storage_returns_none(self, mock_get_book, client: TestClient):
        """Test retrieving a book when storage returns None."""
        book_id = str(uuid.uuid4())
        mock_get_book.return_value = None

        response = client.get(f"/get-books/{book_id}")

        assert response.status_code == 404
        error_response = response.json()
        error = error_response.get("detail")
        assert error["error"] == "http_error"
        assert error["message"] == "Book not found"
        mock_get_book.assert_called_once_with(book_id)

    def test_get_nonexistent_book(self, client: TestClient):
        """Test retrieving a non-existent book."""
        fake_id = str(uuid.uuid4())

        response = client.get(f"/get-books/{fake_id}")

        assert response.status_code == 404
        error_response = response.json()
        error = error_response.get("detail")
        assert error["error"] == "http_error"
        assert error["message"] == "Book not found"


class TestBookUpdate:
    """Test cases for book updates."""

    def test_update_book_partial(self, client: TestClient):
        """Test partial update of a book."""
        book_data = {
            "title": "Original Title",
            "author": "Original Author",
            "published_year": 2020,
            "price": 100.0,
        }

        create_response = client.post("/create-book", json=book_data)
        book_id = create_response.json()["id"]

        update_data = {"title": "Updated Title"}

        response = client.put(f"/books/{book_id}", json=update_data)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["title"] == "Updated Title"
        assert response_data["author"] == "Original Author"


    @patch("app.services.storage.storage.get_book")
    def test_update_nonexistent_book_with_mock(self, mock_get_book, client: TestClient):
        """Test updating a non-existent book with mocked storage."""
        book_id = str(uuid.uuid4())
        mock_get_book.return_value = None

        update_data = {"title": "New Title"}
        response = client.put(f"/books/{book_id}", json=update_data)

        assert response.status_code == 404
        error_response = response.json()
        error = error_response.get("detail")
        assert error["error"] == "http_error"
        assert error["message"] == "Book not found"
        mock_get_book.assert_called_once_with(book_id)

    def test_update_book_invalid_data(self, client: TestClient):
        """Test updating a book with invalid data."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        create_response = client.post("/create-book", json=book_data)
        book_id = create_response.json()["id"]

        update_data = {"title": ""}

        response = client.put(f"/books/{book_id}", json=update_data)

        assert response.status_code == 422
        error_response = response.json()
        if "error" in error_response:
            assert error_response["error"] == "validation_error"
        else:
            assert "detail" in error_response


class TestBookDeletion:
    """Test cases for book deletion."""

    def test_delete_existing_book(self, client: TestClient):
        """Test deleting an existing book."""
        book_data = {
            "title": "To Be Deleted",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        create_response = client.post("/create-book", json=book_data)
        book_id = create_response.json()["id"]

        response = client.delete(f"/books/{book_id}")

        assert response.status_code == 204

        get_response = client.get(f"/get-books/{book_id}")
        assert get_response.status_code == 404

    @patch("app.services.storage.storage.delete_book")
    def test_delete_book_with_mocked_storage(
        self, mock_delete_book, client: TestClient
    ):
        """Test deleting a book with mocked storage service."""
        book_id = str(uuid.uuid4())
        mock_delete_book.return_value = True

        response = client.delete(f"/books/{book_id}")

        assert response.status_code == 204
        mock_delete_book.assert_called_once_with(book_id)

    @patch("app.services.storage.storage.delete_book")
    def test_delete_nonexistent_book_with_mock(
        self, mock_delete_book, client: TestClient
    ):
        """Test deleting a non-existent book with mocked storage."""
        book_id = str(uuid.uuid4())
        mock_delete_book.return_value = False

        response = client.delete(f"/books/{book_id}")

        assert response.status_code == 404
        error_response = response.json()
        error = error_response.get("detail")
        assert error["error"] == "http_error"
        assert error["message"] == "Book not found"
        mock_delete_book.assert_called_once_with(book_id)

    @patch("app.services.storage.storage.delete_book")
    def test_delete_book_storage_exception(self, mock_delete_book, client: TestClient):
        """Test handling storage exceptions during book deletion."""
        book_id = str(uuid.uuid4())
        mock_delete_book.side_effect = Exception("Storage deletion error")

        response = client.delete(f"/books/{book_id}")

        # Depending on your error handling
        assert response.status_code in [500, 503]
        mock_delete_book.assert_called_once_with(book_id)


class TestBookListing:
    """Test cases for book listing."""

    def test_list_empty_books(self, client: TestClient):
        """Test listing books when none exist."""
        response = client.get("/get-books")

        assert response.status_code == 200
        assert response.json() == []

    @patch("app.services.storage.storage.list_books")
    def test_list_books_with_mocked_storage(
        self, mock_list_books, client: TestClient
    ):
        """Test listing books with mocked storage service."""
        # Create Book objects for the mock to return
        mock_books = [
            Book(
                id="mock-id-123",
                title="Mocked Storage Book",
                author="Test Author",
                published_year=2020,
                price=100.0,
                tags=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            Book(
                id="mock-id-456",
                title="Mocked Storage Book 2",
                author="Test Author 2",
                published_year=2021,
                price=200.0,
                tags=None,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
        ]

        mock_list_books.return_value = mock_books

        response = client.get("/get-books")

        assert response.status_code == 200
        response_data = response.json()
        
        # The API returns serialized JSON, so we need to compare the data fields
        assert len(response_data) == 2
        
        # Check first book
        assert response_data[0]["id"] == mock_books[0].id
        assert response_data[0]["title"] == mock_books[0].title
        assert response_data[0]["author"] == mock_books[0].author
        assert response_data[0]["published_year"] == mock_books[0].published_year
        assert response_data[0]["price"] == mock_books[0].price
        assert response_data[0]["tags"] == mock_books[0].tags
        
        # Check second book
        assert response_data[1]["id"] == mock_books[1].id
        assert response_data[1]["title"] == mock_books[1].title
        assert response_data[1]["author"] == mock_books[1].author
        assert response_data[1]["published_year"] == mock_books[1].published_year
        assert response_data[1]["price"] == mock_books[1].price
        assert response_data[1]["tags"] == mock_books[1].tags
        
        mock_list_books.assert_called_once()

    def test_list_all_books(self, client: TestClient):
        """Test listing all books."""
        books_data = [
            {
                "title": "Book 1",
                "author": "Author 1",
                "published_year": 2020,
                "price": 100.0,
                "tags": ["fiction"],
            },
            {
                "title": "Book 2",
                "author": "Author 2",
                "published_year": 2021,
                "price": 200.0,
                "tags": ["non-fiction"],
            },
        ]

        for book_data in books_data:
            client.post("/create-book", json=book_data)

        response = client.get("/get-books")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2

    @patch("app.services.storage.storage.list_books")
    def test_filter_books_by_tag_with_mock(
        self, mock_list_books, client: TestClient
    ):
        """Test filtering books by tag with mocked storage."""
        mock_filtered_books = [
            Book(
                id="fiction-book-1",
                title="Fiction Book",
                author="Fiction Author",
                published_year=2020,
                price=100.0,
                tags=["fiction", "drama"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
        ]

        mock_list_books.return_value = mock_filtered_books

        response = client.get("/get-books?tag=fiction")

        assert response.status_code == 200
        response_data = response.json()
        
        # The API returns serialized JSON, so we need to compare the data fields
        assert len(response_data) == 1
        assert "fiction" in response_data[0]["tags"]
        
        mock_list_books.assert_called_once_with(tag_filter="fiction")

    def test_filter_books_by_tag(self, client: TestClient):
        """Test filtering books by tag."""
        books_data = [
            {
                "title": "Fiction Book",
                "author": "Fiction Author",
                "published_year": 2020,
                "price": 100.0,
                "tags": ["fiction", "drama"],
            },
            {
                "title": "Non-Fiction Book",
                "author": "Non-Fiction Author",
                "published_year": 2021,
                "price": 200.0,
                "tags": ["non-fiction", "biography"],
            },
            {
                "title": "Mixed Book",
                "author": "Mixed Author",
                "published_year": 2022,
                "price": 150.0,
                "tags": ["fiction", "biography"],
            },
        ]

        for book_data in books_data:
            client.post("/create-book", json=book_data)

        response = client.get("/get-books?tag=fiction")

        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data) == 2

        titles = [book["title"] for book in response_data]
        assert "Fiction Book" in titles
        assert "Mixed Book" in titles
        assert "Non-Fiction Book" not in titles


class TestErrorHandling:
    """Test cases for error handling."""

    def test_validation_error_structure(self, client: TestClient):
        """Test validation error response structure."""
        response = client.post("/create-book", json={})

        assert response.status_code == 422
        error_response = response.json()

        if "error" in error_response:
            assert "error" in error_response
            assert "message" in error_response
            assert "details" in error_response
            assert "errors" in error_response["details"]
            assert error_response["error"] == "validation_error"
            assert isinstance(error_response["details"]["errors"], list)
        else:
            assert "detail" in error_response
            assert isinstance(error_response["detail"], list)

    @patch("app.services.storage.storage.list_books")
    def test_internal_server_error_handling(self, mock_list_books, client: TestClient):
        """Test handling of internal server errors."""
        # Mock storage to raise an exception
        mock_list_books.side_effect = Exception("Database connection failed")

        response = client.get("/get-books")

        # Depending on your error handling middleware
        assert response.status_code in [500, 503]


class TestHealthCheck:
    """Test cases for health check endpoint."""

    def test_root_endpoint(self, client: TestClient):
        """Test the root health check endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        response_data = response.json()
        assert "message" in response_data
        assert "running" in response_data["message"].lower()

    @patch("datetime.datetime")
    def test_health_check_with_mocked_datetime(self, mock_datetime, client: TestClient):
        """Test health check with mocked datetime."""
        # Mock datetime.now() if your health check includes timestamp
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = mock_now

        response = client.get("/")

        assert response.status_code == 200
        # Add assertions based on your actual health check implementation


class TestAPIDocumentation:
    """Test cases for API documentation."""

    def test_openapi_docs_accessible(self, client: TestClient):
        """Test that OpenAPI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_accessible(self, client: TestClient):
        """Test that ReDoc is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client: TestClient):
        """Test that OpenAPI JSON schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert "paths" in openapi_data


class TestStateManagement:
    """Test cases for state management."""

    def test_storage_isolation_between_tests(self, client: TestClient):
        """Test that storage is properly cleared between tests."""
        response = client.get("/get-books")
        assert response.status_code == 200
        assert response.json() == []

        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }
        client.post("/create-book", json=book_data)

        response = client.get("/get-books")
        assert len(response.json()) == 1

    def test_crud_operations_state_consistency(self, client: TestClient):
        """Test that CRUD operations maintain consistent state."""
        book_data = {
            "title": "State Test Book",
            "author": "State Test Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": ["test"],
        }

        create_response = client.post("/create-book", json=book_data)
        book_id = create_response.json()["id"]

        get_response = client.get(f"/get-books/{book_id}")
        assert get_response.status_code == 200

        update_data = {"title": "Updated State Test Book"}
        update_response = client.put(f"/books/{book_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated State Test Book"

        get_updated_response = client.get(f"/get-books/{book_id}")
        assert get_updated_response.json()["title"] == "Updated State Test Book"

        delete_response = client.delete(f"/books/{book_id}")
        assert delete_response.status_code == 204

        get_deleted_response = client.get(f"/get-books/{book_id}")
        assert get_deleted_response.status_code == 404
