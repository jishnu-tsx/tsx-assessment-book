from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator
from pydantic.dataclasses import dataclass


# Internal business entity
@dataclass(validate_on_init=True)
class Book:
    """Internal business entity for Book."""

    id: str
    title: str
    author: str
    published_year: int
    price: float
    tags: Optional[List[str]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator("title", "author")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace")
        return v.strip()

    @field_validator("published_year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now().year
        if not (1900 <= v <= current_year):
            raise ValueError("Year must be between 1900 and the current year")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v


# ------------------API Request Model-------------------------


class BookCreate(BaseModel):
    """Model for creating a new book"""

    title: str = Field(
        ...,
        description="Title of the book",
        example="Monty Python & The Holy Grail",
        min_length=1,
    )
    author: str = Field(
        ...,
        description="Name of the book's author",
        example="Terry Gilliam",
        min_length=1,
    )
    published_year: int = Field(
        ...,
        description="Year the book was published",
        example="1994",
        ge=1900,
        le=datetime.now().year,
    )
    price: float = Field(
        ..., description="Price of the book in INR", example="1060", gt=0
    )
    tags: Optional[List[str]] = Field(
        None, description="Additional information of the book", example="[Comedy]"
    )

    @field_validator("title", "author")
    @classmethod
    def non_empty_string(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespace")
        return v.strip()

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "published_year": 1925,
                "price": 399.99,
                "tags": ["classic", "fiction", "literature"],
            }
        },
    }


class BookUpdate(BaseModel):
    """Model for updating a book"""

    title: Optional[str] = Field(None, description="Updated title", min_length=1)
    author: Optional[str] = Field(None, description="Updated author", min_length=1)
    published_year: Optional[int] = Field(
        None, description="Updated year", ge=1900, le=datetime.now().year
    )
    price: Optional[float] = Field(None, description="Updated price in INR", gt=0)
    tags: Optional[List[str]] = Field(None, description="Updated list of tags")

    @field_validator("title", "author")
    @classmethod
    def validate_optional_non_empty_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Field cannot be empty or contain only whitespaces")
        return v.strip() if v else v

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "example": {"title": "The Great Gatsby - Updated Edition", "price": 349.99}
        },
    }


# ------------------API Reponse Model-------------------------


class BookResponse(BaseModel):
    """Model for book responses"""

    id: str = Field(..., description="Unique Identifier of the book")
    title: str = Field(..., description="Titile of the book")
    author: str = Field(..., description="Author of the book")
    published_year: int = Field(..., description="Year the book was published", example="1925")
    price: float = Field(..., description="Price of the book in INR")
    tags: Optional[List[str]] = Field(
        None, description="List of tags for the book eg:[fiction,comedy]"
    )
    created_at: datetime = Field(..., description="Timestamp when the book was created")
    updated_at: datetime = Field(..., description="Timestamp when the book was last updated")

    @classmethod
    def from_book(cls, book: Book) -> "BookResponse":
        return cls(**book.__dict__)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "published_year": 1925,
                "price": 299.99,
                "tags": ["classic", "fiction", "literature"],
            }
        },
    }
