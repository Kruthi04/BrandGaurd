"""BrandGuard API entry point."""
import uvicorn
from app.api.routes import app
from app.config import settings


def main():
    missing = settings.validate()
    if missing:
        print(f"WARNING: Missing configuration keys: {', '.join(missing)}")
        print("Some features will be unavailable. Check your .env file.")
    else:
        print("Configuration validated successfully.")

    print(f"Starting BrandGuard API on http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.api.routes:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )


if __name__ == "__main__":
    main()
