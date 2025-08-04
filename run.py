from app.utils.config import settings
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT)
