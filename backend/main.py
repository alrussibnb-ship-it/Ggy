from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from celery import Celery
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Import our modules
from api.routes import files, tasks, health
from core.config import settings
from core.celery_app import celery_app
from core.storage import StorageManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Audio Processing API",
    description="FastAPI backend for audio/video processing with Celery workers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])

# Mount static directories
storage_dir = Path(settings.STORAGE_ROOT)
uploads_dir = storage_dir / "uploads"
media_dir = storage_dir / "media"
outputs_dir = storage_dir / "outputs"

# Create directories if they don't exist
for directory in [storage_dir, uploads_dir, media_dir, outputs_dir]:
    directory.mkdir(parents=True, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")
app.mount("/outputs", StaticFiles(directory=str(outputs_dir)), name="outputs")

# Storage manager
storage_manager = StorageManager()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Audio Processing API",
        "version": "1.0.0",
        "docs": "/docs",
        "storage_paths": {
            "storage_root": str(storage_dir),
            "uploads": str(uploads_dir),
            "media": str(media_dir),
            "outputs": str(outputs_dir)
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )