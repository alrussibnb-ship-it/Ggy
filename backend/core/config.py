"""Core configuration settings for the application."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Basic app settings
    APP_NAME: str = "Audio Processing API"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Storage settings
    STORAGE_ROOT: str = str(Path(__file__).parent.parent.parent / "storage")
    
    # Redis settings for Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # FFmpeg settings
    FFMPEG_PATH: str = "ffmpeg"  # Default to system ffmpeg
    FFMPEG_TIMEOUT: int = 300  # 5 minutes
    
    # Whisper model settings
    WHISPER_MODEL_SIZE: str = "base"  # tiny, base, small, medium, large
    WHISPER_DEVICE: str = "cpu"  # cpu, cuda
    WHISPER_COMPUTE_TYPE: str = "int8"  # int8, float16, float32
    
    # Translation settings
    TRANSLATION_PROVIDER: str = "googletrans"  # googletrans, azure, aws
    GOOGLETRANS_API_KEY: Optional[str] = None
    
    # Processing settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".mp3", ".mp4", ".wav", ".m4a", ".avi", ".mov", ".mkv"]
    
    # Security settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # GPU settings
    ENABLE_GPU: bool = False
    CUDA_VISIBLE_DEVICES: str = "0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create global settings instance
settings = Settings()