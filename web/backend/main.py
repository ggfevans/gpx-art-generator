"""
FastAPI application for GPX Art Generator web interface.

This module initializes the FastAPI application, sets up routes, middleware,
and static file serving.
"""

import os
import sys
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi

# Import API route handlers
from handlers import router as api_router
from models import ErrorResponse, HealthCheck

# Setup environment variables with defaults
API_VERSION = os.getenv("API_VERSION", "1.0.0")
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
ENV = os.getenv("ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))  # 10MB default

# Create directories
UPLOADS_DIR = Path("./uploads")
OUTPUT_DIR = Path("./output")
LOG_DIR = Path("./logs")

for directory in [UPLOADS_DIR, OUTPUT_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "api.log"),
    ]
)

logger = logging.getLogger("gpx_art_api")

# Initialize FastAPI app with metadata
app = FastAPI(
    title="GPX Art Generator API",
    description="""
    API for generating artwork from GPX files. Upload a GPX file and customize 
    the visualization options to create beautiful route artwork.
    """,
    version=API_VERSION,
    debug=DEBUG_MODE,
    docs_url="/api/docs" if ENV != "production" else None,
    redoc_url="/api/redoc" if ENV != "production" else None,
)


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with a standardized format."""
    logger.warning(f"HTTP error: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": getattr(exc, "code", None)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors with detailed information."""
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        error_messages.append({
            "loc": " -> ".join([str(loc) for loc in error["loc"]]),
            "msg": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error: {json.dumps(error_messages)}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": error_messages,
            "code": "validation_error"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors with graceful error messages."""
    logger.exception(f"Unexpected error: {str(exc)}")
    
    # In production, don't expose detailed error messages
    if ENV == "production":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred", "code": "server_error"}
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"Internal server error: {str(exc)}",
                "traceback": str(exc.__traceback__),
                "code": "server_error"
            }
        )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


# Mount static file server for generated files
app.mount("/files", StaticFiles(directory=str(OUTPUT_DIR)), name="files")


# Include API routes
app.include_router(api_router, prefix="/api")


# Root endpoint for API health check
@app.get("/", response_model=HealthCheck)
async def read_root():
    """API health check endpoint."""
    return HealthCheck(
        status="ok",
        version=API_VERSION
    )


# Custom OpenAPI schema with proper error responses
def custom_openapi():
    """Generate custom OpenAPI schema with error responses."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add standard error responses to all routes
    paths = openapi_schema["paths"]
    for path_name, path_item in paths.items():
        for method_name, method_item in path_item.items():
            if method_name != "parameters":  # Skip non-operation items
                responses = method_item.get("responses", {})
                
                # Add standard error response for validation errors
                responses["422"] = {
                    "description": "Validation Error",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ErrorResponse"
                            }
                        }
                    }
                }
                
                # Add standard error response for internal server errors
                responses["500"] = {
                    "description": "Internal Server Error",
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ErrorResponse"
                            }
                        }
                    }
                }
                
                method_item["responses"] = responses
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info(f"Starting GPX Art Generator API (version {API_VERSION})")
    logger.info(f"Environment: {ENV}")
    logger.info(f"Debug mode: {DEBUG_MODE}")
    logger.info(f"Uploads directory: {UPLOADS_DIR.absolute()}")
    logger.info(f"Output directory: {OUTPUT_DIR.absolute()}")
    
    # Clean up old temporary files on startup
    await cleanup_temp_files()


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("Shutting down GPX Art Generator API")
    
    # Additional cleanup could be added here
    pass


async def cleanup_temp_files():
    """Clean up old temporary files from previous runs."""
    now = datetime.now()
    try:
        # Clean uploads older than 24 hours
        for file_path in UPLOADS_DIR.glob("*"):
            if file_path.is_file():
                file_age = now - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.days > 0:  # Older than 1 day
                    logger.debug(f"Cleaning up old upload: {file_path}")
                    file_path.unlink(missing_ok=True)
        
        # Optionally clean old output files (uncomment if needed)
        # for file_path in OUTPUT_DIR.glob("*"):
        #     if file_path.is_file():
        #         file_age = now - datetime.fromtimestamp(file_path.stat().st_mtime)
        #         if file_age.days > 7:  # Older than 7 days
        #             logger.debug(f"Cleaning up old output: {file_path}")
        #             file_path.unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    """Run the application using uvicorn when executed directly."""
    import uvicorn
    
    # Get environment variables or use defaults
    reload_mode = ENV != "production"
    
    uvicorn.run(
        "main:app", 
        host=HOST, 
        port=PORT, 
        reload=reload_mode,
        log_level=LOG_LEVEL.lower()
    )

