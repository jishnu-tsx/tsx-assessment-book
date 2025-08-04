from typing import Dict, List, Optional
import logging
from app.models.book_models import Book, BookResponse

# Configure logging
logger = logging.getLogger(__name__)


class BookStorageError(Exception):
    """Custom exception for book storage operations"""

    pass


class BookStorage:
    """In-memory storage for books"""

    def __init__(self):
        try:
            self._books: Dict[str, Book] = {}
            logger.info("BookStorage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BookStorage: {e}")
            raise BookStorageError(f"Storage initialization failed: {e}")

    def create_book(self, book: Book) -> Book:
        """Store a new book"""
        try:
            if not book or not hasattr(book, "id"):
                raise ValueError("Invalid book object provided")

            if not book.id:
                raise ValueError("Book ID cannot be empty")

            if book.id in self._books:
                raise ValueError(f"Book with ID '{book.id}' already exists")

            self._books[book.id] = book
            logger.info(f"Book created successfully with ID: {book.id}")
            return book

        except ValueError as e:
            logger.error(f"Validation error creating book: {e}")
            raise BookStorageError(f"Failed to create book: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating book: {e}")
            raise BookStorageError(f"Unexpected error during book creation: {e}")

    def get_book(self, book_id: str) -> Optional[Book]:
        """Retrieve a book by ID"""
        try:
            if not book_id:
                raise ValueError("Book ID cannot be empty")

            book = self._books.get(book_id)
            if book:
                logger.debug(f"Book retrieved successfully: {book_id}")
            else:
                logger.debug(f"Book not found: {book_id}")

            return book

        except ValueError as e:
            logger.error(f"Validation error retrieving book: {e}")
            raise BookStorageError(f"Failed to retrieve book: {e}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving book {book_id}: {e}")
            raise BookStorageError(f"Unexpected error during book retrieval: {e}")

    def update_book(self, book_id: str, book: Book) -> Optional[Book]:
        """Update an existing book"""
        try:
            if not book_id:
                raise ValueError("Book ID cannot be empty")

            if not book or not hasattr(book, "id"):
                raise ValueError("Invalid book object provided")

            if book_id not in self._books:
                logger.warning(f"Attempted to update non-existent book: {book_id}")
                return None

            # Ensure the book object has the correct ID
            book.id = book_id
            self._books[book_id] = book
            logger.info(f"Book updated successfully: {book_id}")
            return book

        except ValueError as e:
            logger.error(f"Validation error updating book: {e}")
            raise BookStorageError(f"Failed to update book: {e}")
        except Exception as e:
            logger.error(f"Unexpected error updating book {book_id}: {e}")
            raise BookStorageError(f"Unexpected error during book update: {e}")

    def delete_book(self, book_id: str) -> bool:
        """Delete a book by ID"""
        try:
            if not book_id:
                raise ValueError("Book ID cannot be empty")

            if book_id in self._books:
                del self._books[book_id]
                logger.info(f"Book deleted successfully: {book_id}")
                return True
            else:
                logger.warning(f"Attempted to delete non-existent book: {book_id}")
                return False

        except ValueError as e:
            logger.error(f"Validation error deleting book: {e}")
            raise BookStorageError(f"Failed to delete book: {e}")
        except Exception as e:
            logger.error(f"Unexpected error deleting book {book_id}: {e}")
            raise BookStorageError(f"Unexpected error during book deletion: {e}")

    def list_books(self, tag_filter: Optional[str] = None) -> List[Book]:
        """List all books, can be filtered by tag"""
        try:
            books = list(self._books.values())

            if tag_filter:
                try:
                    filtered_books = []
                    for book in books:
                        if book.tags and tag_filter in book.tags:
                            filtered_books.append(book)

                    logger.debug(
                        f"Books filtered by tag '{tag_filter}': {len(filtered_books)} found"
                    )
                    return filtered_books

                except AttributeError as e:
                    logger.error(f"Book object missing tags attribute: {e}")
                    raise BookStorageError(f"Invalid book data structure: {e}")

            logger.debug(f"All books listed: {len(books)} found")
            return books

        except Exception as e:
            logger.error(f"Unexpected error listing books: {e}")
            raise BookStorageError(f"Unexpected error during book listing: {e}")

    def clear(self):
        """Clear all books"""
        try:
            book_count = len(self._books)
            self._books.clear()
            logger.info(f"Storage cleared successfully. {book_count} books removed")

        except Exception as e:
            logger.error(f"Error clearing storage: {e}")
            raise BookStorageError(f"Failed to clear storage: {e}")


def book_to_response(book: Book) -> BookResponse:
    """Convert internal Book entity to BookResponse model."""
    try:
        if not book:
            raise ValueError("Book object cannot be None")

        # Validate required attributes
        required_attrs = ["id", "title", "author", "published_year", "price"]
        for attr in required_attrs:
            if not hasattr(book, attr):
                raise AttributeError(f"Book object missing required attribute: {attr}")

        response = BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            published_year=book.published_year,
            price=book.price,
            tags=getattr(book, "tags", None),  # Handle optional tags
        )

        logger.debug(f"Book converted to response format: {book.id}")
        return response

    except (ValueError, AttributeError) as e:
        logger.error(f"Validation error converting book to response: {e}")
        raise BookStorageError(f"Failed to convert book to response: {e}")
    except Exception as e:
        logger.error(f"Unexpected error converting book to response: {e}")
        raise BookStorageError(f"Unexpected error during conversion: {e}")


# Initialize storage instance with error handling
try:
    storage = BookStorage()
except BookStorageError as e:
    logger.critical(f"Failed to initialize global storage instance: {e}")
    # You might want to handle this differently based on your application needs
    storage = None
