from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from app.utils.config import settings
import structlog

from app.utils.exceptions import validation_exception_handler, general_exception_handler
from app.api.routes.books import router as book_router
from app.events.lifecycle import lifespan


# configure_logging()
log = structlog.get_logger()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(book_router)


@app.get("/", summary="Health check")
async def root():
    return {"message": "Book Management API is running"}
