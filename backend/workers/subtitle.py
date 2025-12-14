"""Subtitle processing worker using srt library."""

import os
import logging
from typing import List, Dict, Any, Optional
import srt
from datetime import timedelta

from core.config import settings
from core.storage import StorageManager

logger = logging.getLogger(__name__)


def create_srt_from_segments(
    segments: List[Dict[str, Any]],
    target_language: Optional[str] = None,
    include_timing: bool = True,
    min_duration: float = 1.0
) -> str:
    """Create SRT subtitle file from transcription segments."""
    
    logger.info(f"Creating SRT from {len(segments)} segments")
    
    try:
        subtitle_entries = []
        
        for i, segment in enumerate(segments, 1):
            # Get text (translated if available)
            if target_language and "translation" in segment:
                text = segment["translation"].get("translated_text", segment["text"])
            else:
                text = segment["text"]
            
            # Clean up text
            text = text.strip()
            if not text:
                continue
            
            # Get timing
            start_time = segment.get("start", 0)
            end_time = segment.get("end", start_time + min_duration)
            
            # Ensure minimum duration
            if end_time - start_time < min_duration:
                end_time = start_time + min_duration
            
            # Create SRT entry
            subtitle_entry = srt.Subtitle(
                index=i,
                start=timedelta(seconds=start_time),
                end=timedelta(seconds=end_time),
                content=text
            )
            
            subtitle_entries.append(subtitle_entry)
        
        # Generate SRT content
        srt_content = srt.compose(subtitle_entries)
        
        logger.info(f"Generated SRT with {len(subtitle_entries)} entries")
        return srt_content
        
    except Exception as e:
        logger.error(f"Failed to create SRT: {str(e)}")
        raise


def create_vtt_from_segments(
    segments: List[Dict[str, Any]],
    target_language: Optional[str] = None,
    include_timing: bool = True
) -> str:
    """Create WebVTT subtitle file from transcription segments."""
    
    logger.info(f"Creating WebVTT from {len(segments)} segments")
    
    try:
        vtt_lines = ["WEBVTT", ""]
        
        for segment in segments:
            # Get text (translated if available)
            if target_language and "translation" in segment:
                text = segment["translation"].get("translated_text", segment["text"])
            else:
                text = segment["text"]
            
            # Clean up text
            text = text.strip()
            if not text:
                continue
            
            # Get timing
            start_time = segment.get("start", 0)
            end_time = segment.get("end", 0)
            
            # Format timing for VTT (HH:MM:SS.mmm)
            start_vtt = format_timedelta_vtt(timedelta(seconds=start_time))
            end_vtt = format_timedelta_vtt(timedelta(seconds=end_time))
            
            # Add entry
            vtt_lines.append(f"{start_vtt} --> {end_vtt}")
            vtt_lines.append(text)
            vtt_lines.append("")  # Empty line between entries
        
        vtt_content = "\n".join(vtt_lines)
        
        logger.info(f"Generated WebVTT with {len(segments)} entries")
        return vtt_content
        
    except Exception as e:
        logger.error(f"Failed to create WebVTT: {str(e)}")
        raise


def format_timedelta_vtt(td: timedelta) -> str:
    """Format timedelta for WebVTT (HH:MM:SS.mmm)."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    milliseconds = int(td.microseconds / 1000)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def parse_srt_file(srt_content: str) -> List[Dict[str, Any]]:
    """Parse SRT file content into segments."""
    
    try:
        subtitle_entries = list(srt.parse(srt_content))
        
        segments = []
        for entry in subtitle_entries:
            segment = {
                "index": entry.index,
                "start": entry.start.total_seconds(),
                "end": entry.end.total_seconds(),
                "text": entry.content.strip(),
                "duration": (entry.end - entry.start).total_seconds()
            }
            segments.append(segment)
        
        logger.info(f"Parsed SRT with {len(segments)} entries")
        return segments
        
    except Exception as e:
        logger.error(f"Failed to parse SRT: {str(e)}")
        raise


def merge_subtitle_files(
    srt_files: List[str],
    output_format: str = "srt"
) -> str:
    """Merge multiple subtitle files into one."""
    
    logger.info(f"Merging {len(srt_files)} subtitle files")
    
    try:
        all_segments = []
        
        for file_path in srt_files:
            if not os.path.exists(file_path):
                logger.warning(f"Subtitle file not found: {file_path}")
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse based on format
            if file_path.endswith('.srt'):
                segments = parse_srt_file(content)
            else:
                # For VTT or other formats, you'd need appropriate parsers
                logger.warning(f"Unsupported subtitle format for: {file_path}")
                continue
            
            # Adjust timing to avoid overlaps (simplified approach)
            current_time = all_segments[-1]["end"] if all_segments else 0
            for segment in segments:
                if segment["start"] < current_time:
                    # Shift timing forward
                    time_shift = current_time - segment["start"] + 0.1
                    segment["start"] += time_shift
                    segment["end"] += time_shift
                
                all_segments.append(segment)
                current_time = segment["end"]
        
        # Create merged content
        if output_format.lower() == "srt":
            return create_srt_from_segments(all_segments)
        elif output_format.lower() == "vtt":
            return create_vtt_from_segments(all_segments)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
        
    except Exception as e:
        logger.error(f"Failed to merge subtitle files: {str(e)}")
        raise


def align_subtitles_to_video(
    subtitle_segments: List[Dict[str, Any]],
    video_duration: float,
    target_fps: float = 25.0
) -> List[Dict[str, Any]]:
    """Align subtitle timing to video frames."""
    
    logger.info(f"Aligning {len(subtitle_segments)} segments to video")
    
    try:
        aligned_segments = []
        frame_duration = 1.0 / target_fps
        
        for segment in subtitle_segments:
            # Align start time to nearest frame
            start_frame = round(segment["start"] / frame_duration)
            aligned_start = start_frame * frame_duration
            
            # Align end time to nearest frame
            end_frame = round(segment["end"] / frame_duration)
            aligned_end = min(end_frame * frame_duration, video_duration)
            
            # Ensure minimum duration
            if aligned_end - aligned_start < frame_duration:
                aligned_end = min(aligned_start + frame_duration, video_duration)
            
            aligned_segment = segment.copy()
            aligned_segment["start"] = aligned_start
            aligned_segment["end"] = aligned_end
            aligned_segment["start_frame"] = start_frame
            aligned_segment["end_frame"] = end_frame
            
            aligned_segments.append(aligned_segment)
        
        logger.info(f"Aligned {len(aligned_segments)} segments to video")
        return aligned_segments
        
    except Exception as e:
        logger.error(f"Failed to align subtitles to video: {str(e)}")
        raise


from core.celery_app import celery_app


@celery_app.task
def create_subtitle_task(
    transcription_result: Dict[str, Any],
    target_language: Optional[str] = None,
    format: str = "srt",
    include_timing: bool = True,
    min_duration: float = 1.0
) -> Dict[str, Any]:
    """Celery task to create subtitle file from transcription."""
    
    try:
        segments = transcription_result.get("segments", [])
        
        if not segments:
            raise ValueError("No segments found in transcription result")
        
        # Create subtitle content
        if format.lower() == "srt":
            subtitle_content = create_srt_from_segments(
                segments, target_language, include_timing, min_duration
            )
            filename_suffix = "srt"
        elif format.lower() == "vtt":
            subtitle_content = create_vtt_from_segments(
                segments, target_language, include_timing
            )
            filename_suffix = "vtt"
        else:
            raise ValueError(f"Unsupported subtitle format: {format}")
        
        # Save to file
        storage_manager = StorageManager()
        
        # Generate filename
        original_file = transcription_result.get("file_path", "unknown")
        base_name = os.path.splitext(os.path.basename(original_file))[0]
        filename = f"{base_name}_{target_language or 'original'}.{filename_suffix}"
        
        # Save content
        file_path = storage_manager.save_processed_file(
            subtitle_content.encode('utf-8'),
            filename,
            output_type="subtitles"
        )
        
        result = {
            "subtitles_created": True,
            "format": format,
            "target_language": target_language,
            "num_segments": len(segments),
            "file_path": file_path,
            "filename": filename,
            "content": subtitle_content
        }
        
        logger.info(f"Created {format.upper()} subtitles: {filename}")
        return result
        
    except Exception as e:
        logger.error(f"Subtitle creation failed: {str(e)}")
        raise