"""
Main FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.routers import upload, process, visualize
from app.services.gee_service import initialize_earth_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting RUSLE Web Application...")
    settings.ensure_directories()

    # Initialize Google Earth Engine
    try:
        initialize_earth_engine(settings.gee_project)
        logger.info("Google Earth Engine initialized successfully")
    except Exception as e:
        logger.warning(f"GEE initialization failed: {e}. Some features may be unavailable.")

    yield

    # Shutdown
    logger.info("Shutting down RUSLE Web Application...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Web application for calculating soil loss using the Revised Universal Soil Loss Equation (RUSLE)",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

# Setup templates
templates = Jinja2Templates(directory=str(settings.templates_dir))

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(process.router, prefix="/api", tags=["process"])
app.include_router(visualize.router, prefix="/api", tags=["visualize"])


@app.get("/")
async def root():
    """Redirect to the main application page."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


@app.get("/app")
async def main_page(request: Request):
    """Render the main application page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": settings.app_name}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
