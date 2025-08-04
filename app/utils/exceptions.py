from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.utils.logger import logger


def create_error_response(
    error_type: str, message: str, details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a standardized error response payload."""
    response = {
        "error": error_type,
        "message": message,
    }
    if details:
        response["details"] = details
    return response


def clean_validation_errors(errors: list) -> list:
    """Clean validation errors to make them JSON serializable."""
    cleaned_errors = []
    for error in errors:
        cleaned_error = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input"),
        }

        # Handle the ctx field which might contain non-serializable objects
        if "ctx" in error:
            ctx = error["ctx"]
            cleaned_ctx = {}
            for key, value in ctx.items():
                if isinstance(value, Exception):
                    # Convert exception to string representation
                    cleaned_ctx[key] = str(value)
                else:
                    cleaned_ctx[key] = value
            cleaned_error["ctx"] = cleaned_ctx

        cleaned_errors.append(cleaned_error)

    return cleaned_errors


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handles Pydantic/FastAPI validation errors."""
    # Clean the errors to make them JSON serializable
    cleaned_errors = clean_validation_errors(exc.errors())
    error_details = {"errors": cleaned_errors}

    logger.warning(
        "Validation error occurred",
        path=request.url.path,
        method=request.method,
        errors=cleaned_errors,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=create_error_response(
            "validation_error", "Input validation failed", error_details
        ),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handles unexpected internal errors without exposing internals."""
    logger.error(
        "Unexpected error occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            "internal_error", "An unexpected error occurred. Please try again later."
        ),
    )
