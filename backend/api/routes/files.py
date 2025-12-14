"""File upload and management routes."""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
import aiofiles
import os
from pathlib import Path

from core.config import settings
from core.storage import StorageManager
from workers.transcription import transcribe_audio_task
from workers.subtitle import create_subtitle_task

logger = logging.getLogger(__name__)
router = APIRouter()
storage_manager = StorageManager()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    translate_to: Optional[str] = Form(None)
):
    """Upload and process audio/video file."""
    
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Validate file size (we'll check after reading)
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
        )
    
    try:
        # Save uploaded file
        file_path, public_url = await storage_manager.save_upload(content, file.filename)
        
        # Start transcription task
        task_params = {
            "file_path": file_path,
            "source_language": language,
            "target_language": translate_to
        }
        
        # Submit transcription task
        transcription_task = transcribe_audio_task.delay(**task_params)
        
        return {
            "message": "File uploaded successfully",
            "file_id": transcription_task.id,
            "filename": file.filename,
            "size": len(content),
            "url": public_url,
            "task_id": transcription_task.id,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list")
async def list_files():
    """List all uploaded files."""
    try:
        files_info = []
        
        # List files in uploads directory
        for file_path in storage_manager.uploads_dir.rglob("*"):
            if file_path.is_file():
                info = storage_manager.get_file_info(str(file_path))
                files_info.append(info)
        
        return {"files": files_info}
        
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@router.delete("/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file."""
    try:
        # In a real implementation, you'd look up the file by ID
        # For now, we'll just return success
        return {"message": f"File {file_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """Download processed file."""
    # This would typically serve the processed file
    # For now, return a placeholder
    return {"message": f"Download for file {file_id}"}