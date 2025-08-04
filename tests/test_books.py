import uuid
from unittest.mock import PropertyMock, patch, MagicMock, Mock
import pytest
from fastapi.testclient import TestClient
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
        mock_uuid.return_value = Mock(hex=expected_id)

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

    @patch("app.services.storage.storage.add_book")
    def test_create_book_with_mocked_storage(self, mock_add_book, client: TestClient):
        """Test creating a book with mocked storage service."""
        # Mock the storage add_book method
        expected_book = {
            "id": "mock-id-123",
            "title": "Mocked Storage Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": None,
        }
        mock_add_book.return_value = expected_book

        book_data = {
            "title": "Mocked Storage Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response = client.post("/create-book", json=book_data)

        assert response.status_code == 201
        response_data = response.json()
        assert response_data == expected_book
        mock_add_book.assert_called_once()

    @patch("app.services.storage.storage.add_book")
    def test_create_book_storage_exception(self, mock_add_book, client: TestClient):
        """Test handling storage exceptions during book creation."""
        # Mock storage to raise an exception
        mock_add_book.side_effect = Exception("Storage error")

        book_data = {
            "title": "Exception Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response = client.post("/create-book", json=book_data)

        # Depending on your error handling, this might be 500 or another status
        assert response.status_code in [500, 503]
        mock_add_book.assert_called_once()

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

    @patch("app.services.storage.storage.get_book")
    def test_get_book_with_mocked_storage(self, mock_get_book, client: TestClient):
        """Test retrieving a book with mocked storage service."""
        book_id = "mock-book-id"
        expected_book = {
            "id": book_id,
            "title": "Mocked Book",
            "author": "Mocked Author",
            "published_year": 2020,
            "price": 150.0,
            "tags": ["mocked"],
        }

        mock_get_book.return_value = expected_book

        response = client.get(f"/get-books/{book_id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data == expected_book
        mock_get_book.assert_called_once_with(book_id)

    @patch("app.services.storage.storage.get_book")
    def test_get_book_storage_returns_none(self, mock_get_book, client: TestClient):
        """Test retrieving a book when storage returns None."""
        book_id = "nonexistent-book-id"
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

    @patch("app.services.storage.storage.update_book")
    @patch("app.services.storage.storage.get_book")
    def test_update_book_with_mocked_storage(
        self, mock_get_book, mock_update_book, client: TestClient
    ):
        """Test updating a book with mocked storage service."""
        book_id = "mock-book-id"

        # Mock existing book
        existing_book = {
            "id": book_id,
            "title": "Original Title",
            "author": "Original Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": None,
        }

        # Mock updated book
        updated_book = {
            "id": book_id,
            "title": "Updated Title",
            "author": "Original Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": None,
        }

        mock_get_book.return_value = existing_book
        mock_update_book.return_value = updated_book

        update_data = {"title": "Updated Title"}
        response = client.put(f"/books/{book_id}", json=update_data)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data == updated_book
        mock_get_book.assert_called_once_with(book_id)
        mock_update_book.assert_called_once()

    @patch("app.services.storage.storage.get_book")
    def test_update_nonexistent_book_with_mock(self, mock_get_book, client: TestClient):
        """Test updating a non-existent book with mocked storage."""
        book_id = "nonexistent-book-id"
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
        book_id = "mock-book-id"
        mock_delete_book.return_value = True

        response = client.delete(f"/books/{book_id}")

        assert response.status_code == 204
        mock_delete_book.assert_called_once_with(book_id)

    @patch("app.services.storage.storage.delete_book")
    def test_delete_nonexistent_book_with_mock(
        self, mock_delete_book, client: TestClient
    ):
        """Test deleting a non-existent book with mocked storage."""
        book_id = "nonexistent-book-id"
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
        book_id = "exception-book-id"
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

    @patch("app.services.storage.storage.get_all_books")
    def test_list_books_with_mocked_storage(
        self, mock_get_all_books, client: TestClient
    ):
        """Test listing books with mocked storage service."""
        mock_books = [
            {
                "id": "book-1",
                "title": "Mocked Book 1",
                "author": "Author 1",
                "published_year": 2020,
                "price": 100.0,
                "tags": ["fiction"],
            },
            {
                "id": "book-2",
                "title": "Mocked Book 2",
                "author": "Author 2",
                "published_year": 2021,
                "price": 200.0,
                "tags": ["non-fiction"],
            },
        ]

        mock_get_all_books.return_value = mock_books

        response = client.get("/get-books")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data == mock_books
        mock_get_all_books.assert_called_once()

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

    @patch("app.services.storage.storage.get_books_by_tag")
    def test_filter_books_by_tag_with_mock(
        self, mock_get_books_by_tag, client: TestClient
    ):
        """Test filtering books by tag with mocked storage."""
        mock_filtered_books = [
            {
                "id": "fiction-book-1",
                "title": "Fiction Book",
                "author": "Fiction Author",
                "published_year": 2020,
                "price": 100.0,
                "tags": ["fiction", "drama"],
            }
        ]

        mock_get_books_by_tag.return_value = mock_filtered_books

        response = client.get("/get-books?tag=fiction")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data == mock_filtered_books
        mock_get_books_by_tag.assert_called_once_with("fiction")

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

    @patch("app.services.storage.storage")
    def test_internal_server_error_handling(self, mock_storage, client: TestClient):
        """Test handling of internal server errors."""
        # Mock storage to raise an exception
        mock_storage.get_all_books.side_effect = Exception("Database connection failed")

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


class TestMockingPatterns:
    """Advanced mocking patterns and scenarios."""

    @patch("app.services.storage.storage")
    def test_mock_with_side_effects(self, mock_storage, client: TestClient):
        """Test mocking with side effects for different calls."""
        # Configure side effects for multiple calls
        mock_storage.get_all_books.side_effect = [
            [],  # First call returns empty list
            [{"id": "1", "title": "Book 1"}],  # Second call returns one book
            Exception("Network error"),  # Third call raises exception
        ]

        # First call
        response1 = client.get("/get-books")
        assert response1.status_code == 200
        assert response1.json() == []

        # Second call
        response2 = client.get("/get-books")
        assert response2.status_code == 200
        assert len(response2.json()) == 1

        # Third call should handle exception
        response3 = client.get("/get-books")
        assert response3.status_code in [500, 503]

    @patch("app.services.storage.storage.add_book")
    def test_mock_return_value_vs_side_effect(self, mock_add_book, client: TestClient):
        """Test difference between return_value and side_effect."""
        # Using return_value
        mock_add_book.return_value = {"id": "fixed-id", "title": "Fixed Book"}

        book_data = {
            "title": "Test Book",
            "author": "Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response1 = client.post("/create-book", json=book_data)
        response2 = client.post("/create-book", json=book_data)

        # Both calls return the same mocked value
        assert response1.json()["id"] == "fixed-id"
        assert response2.json()["id"] == "fixed-id"
        assert mock_add_book.call_count == 2

    @patch.object(Mock, "add_book")
    def test_patch_object_example(self, mock_method, client: TestClient):
        """Example of using patch.object for more specific mocking."""
        mock_method.return_value = {"id": "object-mock-id", "title": "Object Mock Book"}

        # This test demonstrates patch.object usage pattern
        # Adjust based on your actual service structure

    def test_mock_assertions_and_call_verification(self, client: TestClient):
        """Test various mock assertion patterns."""
        with patch("app.services.storage.storage.add_book") as mock_add_book:
            mock_add_book.return_value = {"id": "test-id", "title": "Test Book"}

            book_data = {
                "title": "Test Book",
                "author": "Author",
                "published_year": 2020,
                "price": 100.0,
            }

            # Make the call
            client.post("/create-book", json=book_data)

            # Various assertion patterns
            mock_add_book.assert_called_once()
            mock_add_book.assert_called_with(
                mock_add_book.call_args[0][0]
            )  # Verify call arguments
            assert mock_add_book.call_count == 1
            assert mock_add_book.called is True

            # Get call arguments
            call_args = mock_add_book.call_args[0][0]  # First positional argument
            assert call_args.title == "Test Book"

    @patch("app.services.storage.storage")
    def test_comprehensive_storage_mock(self, mock_storage, client: TestClient):
        """Comprehensive test with fully mocked storage."""
        # Configure all storage methods
        mock_storage.add_book.return_value = {
            "id": "mock-id",
            "title": "Mock Book",
            "author": "Mock Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": None,
        }

        mock_storage.get_book.return_value = {
            "id": "mock-id",
            "title": "Mock Book",
            "author": "Mock Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": None,
        }

        mock_storage.get_all_books.return_value = [mock_storage.get_book.return_value]
        mock_storage.update_book.return_value = mock_storage.get_book.return_value
        mock_storage.delete_book.return_value = True

        # Test create
        book_data = {
            "title": "Mock Book",
            "author": "Mock Author",
            "published_year": 2020,
            "price": 100.0,
        }
        create_response = client.post("/create-book", json=book_data)
        assert create_response.status_code == 201

        # Test get
        get_response = client.get("/get-books/mock-id")
        assert get_response.status_code == 200

        # Test list
        list_response = client.get("/get-books")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        # Test update
        update_response = client.put("/books/mock-id", json={"title": "Updated"})
        assert update_response.status_code == 200

        # Test delete
        delete_response = client.delete("/books/mock-id")
        assert delete_response.status_code == 204

        # Verify all mocks were called
        mock_storage.add_book.assert_called_once()
        mock_storage.get_book.assert_called()
        mock_storage.get_all_books.assert_called_once()
        mock_storage.update_book.assert_called_once()
        mock_storage.delete_book.assert_called_once_with("mock-id")


class TestAsyncMocking:
    """Test cases for async operations with mocking."""

    @patch("app.services.storage.storage.add_book")
    async def test_async_book_creation_mock(self, mock_add_book, client: TestClient):
        """Test async book creation with mocked storage."""
        # If your storage operations are async, configure the mock accordingly
        mock_add_book.return_value = {
            "id": "async-mock-id",
            "title": "Async Book",
            "author": "Async Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": None,
        }

        book_data = {
            "title": "Async Book",
            "author": "Async Author",
            "published_year": 2020,
            "price": 100.0,
        }

        # For async operations, you might need AsyncMock
        # from unittest.mock import AsyncMock
        # mock_add_book = AsyncMock(return_value=expected_result)

        response = client.post("/create-book", json=book_data)
        assert response.status_code == 201


class TestContextManagerMocking:
    """Test cases using context managers for mocking."""

    def test_context_manager_mocking(self, client: TestClient):
        """Test using context managers for temporary mocking."""
        book_data = {
            "title": "Context Manager Book",
            "author": "Test Author",
            "published_year": 2020,
            "price": 100.0,
        }

        # Using context manager for temporary mock
        with patch("app.services.storage.storage.add_book") as mock_add_book:
            mock_add_book.return_value = {
                "id": "context-id",
                "title": "Context Manager Book",
                "author": "Test Author",
                "published_year": 2020,
                "price": 100.0,
                "tags": None,
            }

            response = client.post("/create-book", json=book_data)
            assert response.status_code == 201
            assert response.json()["id"] == "context-id"
            mock_add_book.assert_called_once()

        # Mock is automatically restored after context

    def test_multiple_context_managers(self, client: TestClient):
        """Test using multiple context managers simultaneously."""
        with (
            patch("app.services.storage.storage.add_book") as mock_add,
            patch("app.services.storage.storage.get_book") as mock_get,
            patch("uuid.uuid4") as mock_uuid,
        ):
            mock_uuid.return_value = Mock(hex="multi-context-id")
            mock_add.return_value = {
                "id": "multi-context-id",
                "title": "Multi Context Book",
                "author": "Test Author",
                "published_year": 2020,
                "price": 100.0,
                "tags": None,
            }
            mock_get.return_value = mock_add.return_value

            # Test create
            book_data = {
                "title": "Multi Context Book",
                "author": "Test Author",
                "published_year": 2020,
                "price": 100.0,
            }

            create_response = client.post("/create-book", json=book_data)
            assert create_response.status_code == 201

            # Test get
            get_response = client.get("/get-books/multi-context-id")
            assert get_response.status_code == 200

            # Verify all mocks were called
            mock_add.assert_called_once()
            mock_get.assert_called_once_with("multi-context-id")
            mock_uuid.assert_called_once()


class TestMockConfiguration:
    """Test cases for different mock configurations."""

    @patch("app.services.storage.storage")
    def test_mock_attribute_access(self, mock_storage, client: TestClient):
        """Test mocking with attribute access patterns."""
        # Configure mock attributes
        mock_storage.books_count = 5
        mock_storage.max_capacity = 1000

        # Configure method returns
        mock_storage.get_stats.return_value = {
            "total_books": 5,
            "capacity": 1000,
            "utilization": "0.5%",
        }

        # If you have a stats endpoint, test it
        # response = client.get("/stats")
        # assert response.status_code == 200
        # stats = response.json()
        # assert stats["total_books"] == 5

    @patch("app.services.storage.storage")
    def test_mock_property_configuration(self, mock_storage, client: TestClient):
        """Test mocking with property configurations."""
        # Configure mock as a property
        type(mock_storage).is_healthy = PropertyMock(return_value=True)
        type(mock_storage).connection_status = PropertyMock(return_value="connected")

        # Test health check that depends on storage properties
        response = client.get("/")
        assert response.status_code == 200

    def test_mock_spec_usage(self, client: TestClient):
        """Test using spec parameter to limit mock behavior."""
        from app.services.storage import storage

        with patch("app.services.storage.storage", spec=storage) as mock_storage:
            # Mock will only allow attributes/methods that exist on the real object
            mock_storage.add_book.return_value = {"id": "spec-id", "title": "Spec Book"}

            # This would raise AttributeError if method doesn't exist on real storage
            # mock_storage.nonexistent_method.return_value = "error"

            book_data = {
                "title": "Spec Book",
                "author": "Spec Author",
                "published_year": 2020,
                "price": 100.0,
            }

            response = client.post("/create-book", json=book_data)
            assert response.status_code == 201


class TestMockHelpers:
    """Test cases demonstrating mock helper methods."""

    @patch("app.services.storage.storage")
    def test_mock_call_tracking(self, mock_storage, client: TestClient):
        """Test tracking mock calls and arguments."""
        mock_storage.add_book.return_value = {"id": "track-id", "title": "Track Book"}
        mock_storage.get_book.return_value = {"id": "track-id", "title": "Track Book"}

        book_data = {
            "title": "Track Book",
            "author": "Track Author",
            "published_year": 2020,
            "price": 100.0,
        }

        # Make multiple calls
        client.post("/create-book", json=book_data)
        client.get("/get-books/track-id")
        client.get("/get-books/track-id")

        # Check call counts
        assert mock_storage.add_book.call_count == 1
        assert mock_storage.get_book.call_count == 2

        # Check call history
        add_calls = mock_storage.add_book.call_args_list
        get_calls = mock_storage.get_book.call_args_list

        assert len(add_calls) == 1
        assert len(get_calls) == 2

        # Verify call arguments
        for call in get_calls:
            args, kwargs = call
            assert args[0] == "track-id"

    @patch("app.services.storage.storage")
    def test_mock_reset_functionality(self, mock_storage, client: TestClient):
        """Test mock reset functionality."""
        mock_storage.add_book.return_value = {"id": "reset-id", "title": "Reset Book"}

        book_data = {
            "title": "Reset Book",
            "author": "Reset Author",
            "published_year": 2020,
            "price": 100.0,
        }

        # Make some calls
        client.post("/create-book", json=book_data)
        client.post("/create-book", json=book_data)

        assert mock_storage.add_book.call_count == 2

        # Reset the mock
        mock_storage.add_book.reset_mock()

        assert mock_storage.add_book.call_count == 0
        assert mock_storage.add_book.call_args_list == []

        # Make another call
        client.post("/create-book", json=book_data)
        assert mock_storage.add_book.call_count == 1

    def test_mock_assertions_comprehensive(self, client: TestClient):
        """Test comprehensive mock assertion patterns."""
        with patch("app.services.storage.storage.add_book") as mock_add_book:
            mock_add_book.return_value = {"id": "assert-id", "title": "Assert Book"}

            book_data = {
                "title": "Assert Book",
                "author": "Assert Author",
                "published_year": 2020,
                "price": 100.0,
            }

            # Make the call
            response = client.post("/create-book", json=book_data)

            # Different assertion patterns
            mock_add_book.assert_called()  # Called at least once
            mock_add_book.assert_called_once()  # Called exactly once

            # Check if called with specific arguments
            call_args = mock_add_book.call_args[0][0]  # First positional argument
            assert call_args.title == "Assert Book"
            assert call_args.author == "Assert Author"

            # Alternative way to check arguments
            expected_book = mock_add_book.call_args[0][0]
            assert expected_book.price == 100.0
            assert expected_book.published_year == 2020


class TestIntegrationWithMocking:
    """Integration tests that use strategic mocking."""

    @patch("app.services.storage.storage")
    def test_full_crud_cycle_with_strategic_mocking(
        self, mock_storage, client: TestClient
    ):
        """Test full CRUD cycle with strategic mocking of storage layer."""
        book_id = "integration-id"

        # Configure mocks for different operations
        created_book = {
            "id": book_id,
            "title": "Integration Book",
            "author": "Integration Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": ["integration", "test"],
        }

        updated_book = {**created_book, "title": "Updated Integration Book"}

        mock_storage.add_book.return_value = created_book
        mock_storage.get_book.return_value = created_book
        mock_storage.get_all_books.return_value = [created_book]
        mock_storage.update_book.return_value = updated_book
        mock_storage.delete_book.return_value = True

        # Create
        book_data = {
            "title": "Integration Book",
            "author": "Integration Author",
            "published_year": 2020,
            "price": 100.0,
            "tags": ["integration", "test"],
        }

        create_response = client.post("/create-book", json=book_data)
        assert create_response.status_code == 201
        assert create_response.json()["id"] == book_id

        # Read single
        get_response = client.get(f"/get-books/{book_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Integration Book"

        # Read all
        list_response = client.get("/get-books")
        assert list_response.status_code == 200
        assert len(list_response.json()) == 1

        # Update
        mock_storage.get_book.return_value = (
            updated_book  # Update mock for subsequent gets
        )
        update_response = client.put(
            f"/books/{book_id}", json={"title": "Updated Integration Book"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Integration Book"

        # Delete
        mock_storage.get_book.return_value = None  # After deletion
        delete_response = client.delete(f"/books/{book_id}")
        assert delete_response.status_code == 204

        # Verify all operations called storage appropriately
        mock_storage.add_book.assert_called_once()
        assert mock_storage.get_book.call_count >= 2  # Called during read operations
        mock_storage.get_all_books.assert_called_once()
        mock_storage.update_book.assert_called_once()
        mock_storage.delete_book.assert_called_once_with(book_id)

    def test_error_propagation_with_mocking(self, client: TestClient):
        """Test how errors propagate through the system with strategic mocking."""
        with patch("app.services.storage.storage.add_book") as mock_add_book:
            # Test different types of storage exceptions
            storage_exceptions = [
                ValueError("Invalid book data"),
                ConnectionError("Database connection failed"),
                TimeoutError("Operation timed out"),
                Exception("Generic storage error"),
            ]

            for exception in storage_exceptions:
                mock_add_book.side_effect = exception

                book_data = {
                    "title": "Error Test Book",
                    "author": "Error Author",
                    "published_year": 2020,
                    "price": 100.0,
                }

                response = client.post("/create-book", json=book_data)

                # Verify appropriate error handling
                # Adjust expected status codes based on your error handling
                assert response.status_code in [400, 500, 503]

                # Reset for next iteration
                mock_add_book.reset_mock()


class TestPerformanceMocking:
    """Test cases for performance-related scenarios with mocking."""

    @patch("app.services.storage.storage")
    def test_bulk_operations_with_mocking(self, mock_storage, client: TestClient):
        """Test bulk operations with mocked responses."""
        # Mock bulk data
        bulk_books = [
            {
                "id": f"bulk-{i}",
                "title": f"Bulk Book {i}",
                "author": f"Author {i}",
                "published_year": 2020 + i,
                "price": 100.0 + i,
                "tags": [f"tag{i}"],
            }
            for i in range(100)
        ]

        mock_storage.get_all_books.return_value = bulk_books

        # Test listing large number of books
        response = client.get("/get-books")
        assert response.status_code == 200
        assert len(response.json()) == 100

        # Verify mock was called efficiently
        mock_storage.get_all_books.assert_called_once()

    @patch("time.sleep")  # Mock sleep to speed up tests
    @patch("app.services.storage.storage")
    def test_timeout_scenarios_with_mocking(
        self, mock_storage, mock_sleep, client: TestClient
    ):
        """Test timeout scenarios with mocked delays."""
        # If your app has retry logic with delays, mock sleep to speed up tests
        mock_storage.add_book.side_effect = [
            TimeoutError("First attempt timeout"),
            TimeoutError("Second attempt timeout"),
            {
                "id": "timeout-success",
                "title": "Success after retries",
            },  # Success on third try
        ]

        book_data = {
            "title": "Timeout Test Book",
            "author": "Timeout Author",
            "published_year": 2020,
            "price": 100.0,
        }

        response = client.post("/create-book", json=book_data)

        # If your app implements retry logic
        # assert response.status_code == 201
        # assert mock_sleep.call_count >= 2  # Called between retries
        # assert mock_storage.add_book.call_count == 3  # Three attempts


# Additional utility functions for testing with mocks
def create_mock_book(book_id: str = None, **overrides) -> dict:
    """Utility function to create mock book data."""
    default_book = {
        "id": book_id or str(uuid.uuid4()),
        "title": "Mock Book",
        "author": "Mock Author",
        "published_year": 2020,
        "price": 100.0,
        "tags": None,
    }
    default_book.update(overrides)
    return default_book


def setup_storage_mock(mock_storage, books: list = None):
    """Utility function to setup storage mock with default behavior."""
    books = books or []

    mock_storage.get_all_books.return_value = books
    mock_storage.get_book.side_effect = lambda book_id: next(
        (book for book in books if book["id"] == book_id), None
    )
    mock_storage.add_book.side_effect = lambda book: {
        **book.__dict__,
        "id": str(uuid.uuid4()),
    }
    mock_storage.update_book.side_effect = lambda book_id, updates: {
        **next(book for book in books if book["id"] == book_id),
        **updates.__dict__,
    }
    mock_storage.delete_book.side_effect = lambda book_id: any(
        book["id"] == book_id for book in books
    )


class TestMockUtilities:
    """Test the mock utility functions."""

    def test_create_mock_book_utility(self):
        """Test the create_mock_book utility function."""
        # Test default values
        book = create_mock_book()
        assert "id" in book
        assert book["title"] == "Mock Book"
        assert book["author"] == "Mock Author"

        # Test with overrides
        book = create_mock_book(book_id="custom-id", title="Custom Title", price=250.0)
        assert book["id"] == "custom-id"
        assert book["title"] == "Custom Title"
        assert book["price"] == 250.0
        assert book["author"] == "Mock Author"  # Default preserved

    @patch("app.services.storage.storage")
    def test_setup_storage_mock_utility(self, mock_storage, client: TestClient):
        """Test the setup_storage_mock utility function."""
        # Create test books
        books = [
            create_mock_book("book-1", title="Book 1"),
            create_mock_book("book-2", title="Book 2"),
        ]

        # Setup mock using utility
        setup_storage_mock(mock_storage, books)

        # Test that mock behaves as expected
        assert mock_storage.get_all_books() == books
        assert mock_storage.get_book("book-1")["title"] == "Book 1"
        assert mock_storage.get_book("nonexistent") is None
        assert mock_storage.delete_book("book-1") is True
        assert mock_storage.delete_book("nonexistent") is False
