"""Text translation worker using various translation services."""

import logging
from typing import Optional, Dict, Any

from googletrans import Translator
from transformers import pipeline

from core.config import settings

logger = logging.getLogger(__name__)

# Global translator instance
_translator = None


def get_translator():
    """Get or create translator instance."""
    global _translator
    
    if _translator is None:
        if settings.TRANSLATION_PROVIDER == "googletrans":
            _translator = Translator()
        elif settings.TRANSLATION_PROVIDER == "transformers":
            _translator = pipeline(
                "translation",
                model="facebook/m2m100_418M"  # You can make this configurable
            )
        else:
            raise ValueError(f"Unsupported translation provider: {settings.TRANSLATION_PROVIDER}")
    
    return _translator


def translate_text(
    text: str,
    source_language: str,
    target_language: str,
    **kwargs
) -> Dict[str, Any]:
    """Translate text using the configured translation service."""
    
    logger.info(f"Translating text from {source_language} to {target_language}")
    
    try:
        translator = get_translator()
        
        if settings.TRANSLATION_PROVIDER == "googletrans":
            # Use googletrans
            result = translator.translate(
                text,
                src=source_language,
                dest=target_language
            )
            
            return {
                "original_text": text,
                "translated_text": result.text,
                "source_language": source_language,
                "target_language": target_language,
                "provider": "googletrans",
                "confidence": getattr(result, 'confidence', None)
            }
            
        elif settings.TRANSLATION_PROVIDER == "transformers":
            # Use transformers pipeline
            result = translator(
                text,
                src_lang=source_language,
                tgt_lang=target_language,
                **kwargs
            )
            
            # Handle different pipeline output formats
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            
            return {
                "original_text": text,
                "translated_text": result.get("translation_text", ""),
                "source_language": source_language,
                "target_language": target_language,
                "provider": "transformers",
                "score": result.get("score", None)
            }
            
        else:
            raise ValueError(f"Unsupported translation provider: {settings.TRANSLATION_PROVIDER}")
        
    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise


def translate_batch(
    texts: list,
    source_language: str,
    target_language: str,
    **kwargs
) -> Dict[str, Any]:
    """Translate multiple texts in batch."""
    
    logger.info(f"Translating {len(texts)} texts from {source_language} to {target_language}")
    
    try:
        translator = get_translator()
        
        translated_texts = []
        
        if settings.TRANSLATION_PROVIDER == "googletrans":
            # googletrans doesn't have native batch support, so we translate individually
            for text in texts:
                result = translator.translate(
                    text,
                    src=source_language,
                    dest=target_language
                )
                translated_texts.append({
                    "original_text": text,
                    "translated_text": result.text,
                    "confidence": getattr(result, 'confidence', None)
                })
                
        elif settings.TRANSLATION_PROVIDER == "transformers":
            # For transformers, we might be able to process multiple texts
            results = translator(
                texts,
                src_lang=source_language,
                tgt_lang=target_language,
                **kwargs
            )
            
            if isinstance(results, list):
                for original_text, result in zip(texts, results):
                    if isinstance(result, list) and len(result) > 0:
                        result = result[0]
                    translated_texts.append({
                        "original_text": original_text,
                        "translated_text": result.get("translation_text", ""),
                        "score": result.get("score", None)
                    })
            else:
                # Single result returned
                translated_texts.append({
                    "original_text": texts[0],
                    "translated_text": results.get("translation_text", ""),
                    "score": results.get("score", None)
                })
        
        return {
            "source_language": source_language,
            "target_language": target_language,
            "provider": settings.TRANSLATION_PROVIDER,
            "translations": translated_texts
        }
        
    except Exception as e:
        logger.error(f"Batch translation failed: {str(e)}")
        raise


from core.celery_app import celery_app


@celery_app.task
def translate_text_task(
    text: str,
    source_language: str,
    target_language: str,
    **kwargs
) -> Dict[str, Any]:
    """Celery task for text translation."""
    return translate_text(
        text=text,
        source_language=source_language,
        target_language=target_language,
        **kwargs
    )


@celery_app.task
def translate_batch_task(
    texts: list,
    source_language: str,
    target_language: str,
    **kwargs
) -> Dict[str, Any]:
    """Celery task for batch text translation."""
    return translate_batch(
        texts=texts,
        source_language=source_language,
        target_language=target_language,
        **kwargs
    )