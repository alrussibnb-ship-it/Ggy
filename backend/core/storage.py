"""Storage management utilities."""

import os
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from uuid import uuid4
import aiofiles
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class StorageManager:
    """Manages file storage operations."""
    
    def __init__(self):
        self.storage_root = Path(settings.STORAGE_ROOT)
        self.uploads_dir = self.storage_root / "uploads"
        self.media_dir = self.storage_root / "media"
        self.outputs_dir = self.storage_root / "outputs"
        
        # Create directories if they don't exist
        for directory in [self.uploads_dir, self.media_dir, self.outputs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_unique_filename(self, original_filename: str, directory: Path) -> str:
        """Generate a unique filename to avoid conflicts."""
        ext = Path(original_filename).suffix
        unique_name = f"{uuid4().hex}{ext}"
        return directory / unique_name
    
    async def save_upload(self, file_content: bytes, original_filename: str) -> Tuple[str, str]:
        """Save uploaded file and return the path and URL."""
        file_path = self.get_unique_filename(original_filename, self.uploads_dir)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        # Return relative path from storage root and public URL
        relative_path = file_path.relative_to(self.storage_root)
        public_url = f"/{relative_path.as_posix()}"
        
        logger.info(f"Saved upload: {original_filename} -> {file_path}")
        return str(file_path), public_url
    
    def save_processed_file(self, content: bytes, filename: str, output_type: str = "output") -> str:
        """Save processed content to outputs directory."""
        output_dir = self.outputs_dir / output_type
        output_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = output_dir / filename
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Saved processed file: {filename} -> {file_path}")
        return str(file_path)
    
    def move_to_media(self, file_path: str) -> str:
        """Move file to media directory for permanent storage."""
        source_path = Path(file_path)
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Create media subdirectory based on file type
        ext = source_path.suffix.lower()
        if ext in ['.mp3', '.wav', '.m4a']:
            media_subdir = "audio"
        elif ext in ['.mp4', '.avi', '.mov', '.mkv']:
            media_subdir = "video"
        else:
            media_subdir = "other"
        
        media_dir = self.media_dir / media_subdir
        media_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename in media directory
        unique_filename = self.get_unique_filename(source_path.name, media_dir)
        shutil.move(str(source_path), str(unique_filename))
        
        logger.info(f"Moved file to media: {source_path} -> {unique_filename}")
        return str(unique_filename)
    
    def get_file_info(self, file_path: str) -> dict:
        """Get file information."""
        path = Path(file_path)
        if not path.exists():
            return {}
        
        stat = path.stat()
        return {
            "filename": path.name,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "is_file": path.is_file(),
            "is_dir": path.is_dir()
        }
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours."""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        cleaned_files = 0
        cleaned_size = 0
        
        # Clean uploads directory
        for file_path in self.uploads_dir.rglob("*"):
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    cleaned_files += 1
                    cleaned_size += file_size
        
        logger.info(f"Cleaned up {cleaned_files} files ({cleaned_size} bytes)")
        return cleaned_files, cleaned_size