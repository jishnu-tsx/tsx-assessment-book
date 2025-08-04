import structlog
import os
import glob
from contextlib import asynccontextmanager
from pathlib import Path

log = structlog.get_logger()


async def startup_tasks():
    """Execute startup tasks."""
    log.info("Application startup")

    # Clear old log files
    await clear_old_logs()

    # Add other startup tasks here
    # await init_database()
    # await load_config()


async def shutdown_tasks():
    """Execute shutdown tasks."""
    log.info("Application shutdown")

    # Add cleanup tasks here
    # await close_database_connections()
    # await cleanup_temp_files()


async def clear_old_logs():
    """Clear old log files on startup."""
    try:
        log_dir = Path("logs")
        if log_dir.exists():
            # Remove log files older than 7 days or clear all - adjust as needed
            log_files = glob.glob("logs/*.log*")
            for log_file in log_files:
                try:
                    os.remove(log_file)
                    log.info(f"Removed old log file: {log_file}")
                except OSError as e:
                    log.warning(f"Could not remove log file {log_file}: {e}")

        # Ensure logs directory exists
        log_dir.mkdir(exist_ok=True)
        log.info("Log cleanup completed")

    except Exception as e:
        log.error(f"Error during log cleanup: {e}")


@asynccontextmanager
async def lifespan(app):
    """Handle startup and shutdown events."""
    # Startup
    await startup_tasks()

    yield

    # Shutdown
    await shutdown_tasks()
