"""Task management routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging

from core.celery_app import celery_app

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a Celery task."""
    try:
        task = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task.status,
            "result": task.result if task.successful() else None,
            "traceback": task.traceback if task.failed() else None
        }
        
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@router.post("/cancel/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task."""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Task {task_id} cancelled"}
        
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")


@router.get("/active")
async def get_active_tasks():
    """Get list of active tasks."""
    try:
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()
        
        return {"active_tasks": active_tasks}
        
    except Exception as e:
        logger.error(f"Error getting active tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get active tasks: {str(e)}")


@router.get("/worker-status")
async def get_worker_status():
    """Get worker status information."""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        registered_tasks = inspect.registered()
        
        return {
            "worker_stats": stats,
            "registered_tasks": registered_tasks
        }
        
    except Exception as e:
        logger.error(f"Error getting worker status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get worker status: {str(e)}")


@router.get("/queue-info")
async def get_queue_info():
    """Get information about task queues."""
    # This is a simplified version - in production you'd inspect Redis directly
    try:
        return {
            "message": "Queue information would be implemented here",
            "queues": ["celery", "transcription", "translation", "subtitle"]
        }
        
    except Exception as e:
        logger.error(f"Error getting queue info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue info: {str(e)}")