import logging
import structlog
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from app.utils.config import settings


def configure_logging():
    """Configure structured logging with rotation."""
    # Create logs directory
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Setup handlers
    handlers = []

    # Console handler
    handlers.append(logging.StreamHandler())

    # File handler with rotation
    log_file_path = os.path.join(log_dir, "app.log")

    if settings.LOG_ROTATION_TYPE == "size":
        # Rotate by file size
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=settings.LOG_MAX_BYTES,  # e.g., 10MB
            backupCount=settings.LOG_BACKUP_COUNT,  # Keep 5 backup files
            encoding="utf-8",
        )
    else:
        # Rotate by time (daily, weekly, etc.)
        file_handler = TimedRotatingFileHandler(
            log_file_path,
            when=settings.LOG_ROTATION_WHEN,  # 'midnight', 'W0' (weekly), etc.
            interval=settings.LOG_ROTATION_INTERVAL,
            backupCount=settings.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )

    handlers.append(file_handler)

    # Configure basic logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(message)s",
        handlers=handlers,
    )

    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(
            fmt=settings.LOG_TIMESTAMP_FORMAT, utc=settings.LOG_USE_UTC
        ),
        structlog.processors.UnicodeDecoder(),
    ]

    # Add appropriate renderer based on environment
    if settings.DEBUG:
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Get logger instance
logger = structlog.get_logger("book_api")
