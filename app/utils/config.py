from typing import Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Book Management API"
    DEBUG: bool = False

    HOST: str = "127.0.0.1"
    PORT: int = 8000
    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_ROTATION_TYPE: Literal["size", "time"] = "size"

    # Size-based rotation settings
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5

    # Time-based rotation settings
    LOG_ROTATION_WHEN: Literal[
        "S", "M", "H", "D", "midnight", "W0", "W1", "W2", "W3", "W4", "W5", "W6"
    ] = "midnight"
    LOG_ROTATION_INTERVAL: int = 1

    # Log formatting
    LOG_TIMESTAMP_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    LOG_USE_UTC: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
