"""Audio transcription worker using faster-whisper."""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import threading

from faster_whisper import WhisperModel

from core.config import settings
from core.storage import StorageManager

logger = logging.getLogger(__name__)

# Global model instance (loaded once per worker process)
_model_instance = None
_model_lock = threading.Lock()


def get_whisper_model():
    """Get or create Whisper model instance (singleton per worker)."""
    global _model_instance
    
    if _model_instance is None:
        with _model_lock:
            if _model_instance is None:
                logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL_SIZE}")
                try:
                    _model_instance = WhisperModel(
                        settings.WHISPER_MODEL_SIZE,
                        device=settings.WHISPER_DEVICE,
                        compute_type=settings.WHISPER_COMPUTE_TYPE
                    )
                    logger.info("Whisper model loaded successfully")
                except Exception as e:
                    logger.error(f"Failed to load Whisper model: {str(e)}")
                    raise
    
    return _model_instance


def transcribe_audio(
    file_path: str,
    source_language: Optional[str] = None,
    target_language: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Transcribe audio file using Whisper."""
    
    # Validate file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    logger.info(f"Starting transcription for: {file_path}")
    
    try:
        # Get Whisper model (singleton per worker)
        model = get_whisper_model()
        
        # Transcribe
        segments, info = model.transcribe(
            file_path,
            language=source_language,
            task="transcribe",
            **kwargs
        )
        
        # Collect transcription results
        transcription_result = {
            "text": "",
            "segments": [],
            "language": info.language,
            "language_probability": info.language_probability,
            "duration": info.duration,
            "file_path": file_path
        }
        
        full_text = []
        for segment in segments:
            segment_data = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": []
            }
            
            # Add word-level timing if available
            if hasattr(segment, 'words') and segment.words:
                for word in segment.words:
                    word_data = {
                        "word": word.word.strip(),
                        "start": word.start,
                        "end": word.end,
                        "probability": word.probability
                    }
                    segment_data["words"].append(word_data)
            
            transcription_result["segments"].append(segment_data)
            full_text.append(segment.text.strip())
        
        transcription_result["text"] = " ".join(full_text)
        
        # Save transcription to file
        if target_language:
            # This would trigger translation
            from workers.translation import translate_text
            translation_result = translate_text(
                transcription_result["text"],
                transcription_result["language"],
                target_language
            )
            transcription_result["translation"] = translation_result
        
        logger.info(f"Transcription completed for: {file_path}")
        logger.info(f"Detected language: {transcription_result['language']} "
                   f"(confidence: {transcription_result['language_probability']:.2f})")
        logger.info(f"Transcription: {transcription_result['text'][:100]}...")
        
        return transcription_result
        
    except Exception as e:
        logger.error(f"Transcription failed for {file_path}: {str(e)}")
        raise


from core.celery_app import celery_app


@celery_app.task
def transcribe_audio_task(
    file_path: str,
    source_language: Optional[str] = None,
    target_language: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Celery task for audio transcription."""
    return transcribe_audio(
        file_path=file_path,
        source_language=source_language,
        target_language=target_language,
        **kwargs
    )