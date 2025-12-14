"""Health check routes."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
import sys
import os
from pathlib import Path

from core.config import settings
from core.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": settings.VERSION,
        "app_name": settings.APP_NAME
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check including dependencies."""
    health_status = {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
        "checks": {}
    }
    
    # Check Python version
    health_status["checks"]["python_version"] = {
        "status": "ok",
        "version": sys.version,
        "executable": sys.executable
    }
    
    # Check storage directories
    storage_checks = {}
    for name, path in [
        ("storage_root", settings.STORAGE_ROOT),
        ("uploads", f"{settings.STORAGE_ROOT}/uploads"),
        ("media", f"{settings.STORAGE_ROOT}/media"),
        ("outputs", f"{settings.STORAGE_ROOT}/outputs")
    ]:
        try:
            path_obj = Path(path)
            exists = path_obj.exists()
            writable = path_obj.exists() and os.access(path_obj, os.W_OK) if exists else False
            storage_checks[name] = {
                "status": "ok" if exists and writable else "error",
                "path": str(path),
                "exists": exists,
                "writable": writable
            }
        except Exception as e:
            storage_checks[name] = {
                "status": "error",
                "path": str(path),
                "error": str(e)
            }
    
    health_status["checks"]["storage"] = storage_checks
    
    # Check Redis connection
    try:
        redis_available = False
        try:
            import redis
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            redis_available = True
        except Exception:
            redis_available = False
        
        health_status["checks"]["redis"] = {
            "status": "ok" if redis_available else "error",
            "url": settings.REDIS_URL,
            "available": redis_available
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Celery workers
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        celery_status = "ok" if stats else "error"
        
        health_status["checks"]["celery"] = {
            "status": celery_status,
            "workers": len(stats) if stats else 0
        }
    except Exception as e:
        health_status["checks"]["celery"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check FFmpeg
    try:
        import subprocess
        import shutil
        
        ffmpeg_path = shutil.which(settings.FFMPEG_PATH)
        if ffmpeg_path:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            ffmpeg_available = result.returncode == 0
        else:
            ffmpeg_available = False
        
        health_status["checks"]["ffmpeg"] = {
            "status": "ok" if ffmpeg_available else "error",
            "path": ffmpeg_path or settings.FFMPEG_PATH,
            "available": ffmpeg_available
        }
    except Exception as e:
        health_status["checks"]["ffmpeg"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check Whisper model
    try:
        from faster_whisper import WhisperModel
        
        whisper_available = False
        try:
            # Just test if we can import and create a model
            model = WhisperModel(settings.WHISPER_MODEL_SIZE, device=settings.WHISPER_DEVICE)
            whisper_available = True
            del model  # Clean up
        except Exception:
            whisper_available = False
        
        health_status["checks"]["whisper"] = {
            "status": "ok" if whisper_available else "error",
            "model_size": settings.WHISPER_MODEL_SIZE,
            "device": settings.WHISPER_DEVICE,
            "available": whisper_available
        }
    except Exception as e:
        health_status["checks"]["whisper"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Overall status
    failed_checks = [
        check_name for check_name, check_data in health_status["checks"].items()
        if check_data["status"] != "ok"
    ]
    
    if failed_checks:
        health_status["status"] = "degraded" if len(failed_checks) == 1 else "unhealthy"
        health_status["failed_checks"] = failed_checks
    
    return health_status


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes-style health probes."""
    try:
        # Check critical dependencies
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        
        return {"status": "ready"}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes-style health probes."""
    return {"status": "alive"}