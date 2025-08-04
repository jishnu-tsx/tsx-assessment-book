from fastapi import APIRouter, HTTPException, status, Query
import uuid
from typing import List, Optional
from pydantic import ValidationError

from app.models.book_models import Book, BookCreate, BookUpdate, BookResponse
from app.services.storage import storage, book_to_response
from app.utils.logger import logger
from app.utils.exceptions import create_error_response

router = APIRouter()


@router.post(
    "/create-book",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new book",
)
async def create_book(book_data: BookCreate) -> BookResponse:
    """Create a new book"""
    try:
        book_id = str(uuid.uuid4())

        logger.debug(
            "Creating a new book",
            book_id=str(book_id),
            title=book_data.title,
            author=book_data.author,
        )

        book = Book(
            id=book_id,
            title=book_data.title,
            author=book_data.author,
            published_year=book_data.published_year,
            price=book_data.price,
            tags=book_data.tags,
        )

        created_book = storage.create_book(book)
        logger.debug(
            "Book created successfully",
            book_id=str(created_book.id),
            title=created_book.title,
        )

        return book_to_response(created_book)

    except ValidationError as e:
        logger.error("Validation error while creating book", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=create_error_response(
                "validation_error", f"Invalid book data: {str(e)}"
            ),
        )
    except ValueError as e:
        logger.error("Value error while creating book", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=create_error_response(
                "validation_error", f"Invalid input: {str(e)}"
            ),
        )
    except Exception as e:
        logger.error(
            "Unexpected error while creating book",
            error=str(e),
            book_data=book_data.model_dump(),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("internal_error", "Failed to create book"),
        )


@router.get(
    "/get-books/{book_id}",
    response_model=BookResponse,
    summary="Get a book by ID",
    description="Retrieves a specific book by its UUID.",
)
async def get_book(book_id: str) -> BookResponse:
    """Get a book by its ID"""
    try:
        logger.debug("Retrieving book", book_id=book_id)

        # Validate UUID format
        try:
            uuid.UUID(book_id)
        except ValueError:
            logger.warning("Invalid UUID format", book_id=book_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    "validation_error", "Invalid book ID format"
                ),
            )

        book = storage.get_book(book_id)
        if not book:
            logger.warning("Book not found", book_id=book_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response("http_error", "Book not found"),
            )

        logger.debug("Book retrieved successfully", book_id=book_id)
        return book_to_response(book)

    except HTTPException:
        # Re-raise HTTP exceptions (they're already handled properly)
        raise
    except Exception as e:
        logger.error(
            "Unexpected error while retrieving book", error=str(e), book_id=book_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("internal_error", "Failed to retrieve book"),
        )


@router.put(
    "/books/{book_id}",
    response_model=BookResponse,
    summary="Update a book",
    description="Updates an existing book. All fields are optional in the request body.",
)
async def update_book(book_id: str, book_update: BookUpdate) -> BookResponse:
    """Update an existing book."""
    try:
        logger.debug("Updating book", book_id=book_id)

        # Validate UUID format
        try:
            uuid.UUID(book_id)
        except ValueError:
            logger.warning("Invalid UUID format for update", book_id=book_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    "validation_error", "Invalid book ID format"
                ),
            )

        existing_book = storage.get_book(book_id)
        if not existing_book:
            logger.warning("Book not found for update", book_id=book_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response("http_error", "Book not found"),
            )

        # Update only provided fields
        update_data = book_update.model_dump(exclude_unset=True)

        updated_book = Book(
            id=book_id,
            title=update_data.get("title", existing_book.title),
            author=update_data.get("author", existing_book.author),
            published_year=update_data.get(
                "published_year", existing_book.published_year
            ),
            price=update_data.get("price", existing_book.price),
            tags=update_data.get("tags", existing_book.tags),
        )

        storage.update_book(book_id, updated_book)

        logger.info(
            "Book updated successfully",
            book_id=str(book_id),
            updated_fields=list(update_data.keys()),
        )

        return book_to_response(updated_book)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValidationError as e:
        logger.error(
            "Validation error while updating book", error=str(e), book_id=book_id
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=create_error_response(
                "validation_error", f"Invalid update data: {str(e)}"
            ),
        )
    except ValueError as e:
        logger.error("Value error while updating book", error=str(e), book_id=book_id)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=create_error_response(
                "validation_error", f"Invalid input: {str(e)}"
            ),
        )
    except Exception as e:
        logger.error(
            "Unexpected error while updating book", error=str(e), book_id=book_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("internal_error", "Failed to update book"),
        )


@router.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a book",
    description="Deletes a book by its UUID.",
)
async def delete_book(book_id: str):
    """Delete a book by its ID."""
    try:
        logger.debug("Deleting book", book_id=book_id)

        # Validate UUID format
        try:
            uuid.UUID(book_id)
        except ValueError:
            logger.warning("Invalid UUID format for deletion", book_id=book_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=create_error_response(
                    "validation_error", "Invalid book ID format"
                ),
            )

        deleted = storage.delete_book(book_id)
        if not deleted:
            logger.warning("Book not found for deletion", book_id=book_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=create_error_response("http_error", "Book not found"),
            )

        logger.info("Book deleted successfully", book_id=book_id)
        return {"status": "SUCCESS", "message": "Book deleted successfully"}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error while deleting book", error=str(e), book_id=book_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("internal_error", "Failed to delete book"),
        )


@router.get(
    "/get-books",
    response_model=List[BookResponse],
    summary="List all books",
    description="Retrieves all books. Optionally filter by tag",
)
async def list_books(
    tag: Optional[str] = Query(None, description="Filter books by tag"),
) -> List[BookResponse]:
    """List all books, optionally filtered by tag"""
    try:
        logger.debug("Listing books", tag_filter=tag)

        books = storage.list_books(tag_filter=tag)
        logger.debug("Books retrieved successfully", count=len(books), tag_filter=tag)

        return [book_to_response(book) for book in books]

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Unexpected error while listing books", error=str(e), tag_filter=tag
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=create_error_response("internal_error", "Failed to retrieve books"),
        )
