"""FastAPI application with GPU/CUDA and FFmpeg configuration support."""

import asyncio
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import torch
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import BotConfig
from .logger import get_logger

logger = get_logger(__name__)


class GPUInfo(BaseModel):
    """GPU information model."""
    cuda_available: bool
    cuda_version: Optional[str] = None
    gpu_count: int = 0
    gpu_name: Optional[str] = None
    gpu_memory_total: Optional[int] = None
    gpu_memory_used: Optional[int] = None
    gpu_utilization: Optional[float] = None


class FFmpegInfo(BaseModel):
    """FFmpeg information model."""
    ffmpeg_available: bool
    ffmpeg_version: Optional[str] = None
    ffprobe_available: bool
    libass_support: bool
    subtitle_support: bool
    ffmpeg_path: Optional[str] = None
    error_message: Optional[str] = None


class CUDAInfo(BaseModel):
    """CUDA information model."""
    nvcc_available: bool
    nvcc_version: Optional[str] = None
    cuda_path: Optional[str] = None
    cuda_version: Optional[str] = None
    error_message: Optional[str] = None


class SystemInfo(BaseModel):
    """System information model."""
    platform: str
    architecture: str
    python_version: str
    gpu_info: GPUInfo
    ffmpeg_info: FFmpegInfo
    cuda_info: CUDAInfo
    fallback_to_cpu: bool


class GPUDetector:
    """GPU and CUDA detection utility."""
    
    def __init__(self):
        self.cuda_available = torch.cuda.is_available()
        self.cuda_version = None
        self.gpu_count = 0
        self.gpu_name = None
        self.gpu_memory_total = None
        self.gpu_memory_used = None
        self.gpu_utilization = None
        
    def detect_cuda(self) -> Tuple[bool, Optional[str]]:
        """Detect CUDA availability and version."""
        if not self.cuda_available:
            return False, None
            
        try:
            cuda_version = torch.version.cuda
            return True, cuda_version
        except Exception as e:
            logger.warning(f"Failed to detect CUDA version: {e}")
            return True, "unknown"
    
    def detect_gpu_info(self) -> GPUInfo:
        """Detect comprehensive GPU information."""
        cuda_available, cuda_version = self.detect_cuda()
        
        if cuda_available and torch.cuda.device_count() > 0:
            try:
                self.gpu_count = torch.cuda.device_count()
                self.gpu_name = torch.cuda.get_device_name(0)
                
                if hasattr(torch.cuda, 'get_device_properties'):
                    props = torch.cuda.get_device_properties(0)
                    self.gpu_memory_total = props.total_memory
                    
                # Get current memory usage if available
                try:
                    self.gpu_memory_used = torch.cuda.memory_allocated(0)
                except Exception:
                    pass
                    
                # Try to get GPU utilization (requires nvidia-ml-py or similar)
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    self.gpu_utilization = float(util.gpu)
                    pynvml.nvmlShutdown()
                except ImportError:
                    logger.info("pynvml not available, skipping GPU utilization detection")
                except Exception as e:
                    logger.warning(f"Failed to detect GPU utilization: {e}")
                    
            except Exception as e:
                logger.warning(f"Failed to detect detailed GPU info: {e}")
                
        return GPUInfo(
            cuda_available=cuda_available,
            cuda_version=cuda_version,
            gpu_count=self.gpu_count,
            gpu_name=self.gpu_name,
            gpu_memory_total=self.gpu_memory_total,
            gpu_memory_used=self.gpu_memory_used,
            gpu_utilization=self.gpu_utilization
        )


class FFMpegValidator:
    """FFmpeg validation and configuration utility."""
    
    def __init__(self):
        self.ffmpeg_path = None
        self.ffprobe_path = None
        
    def find_ffmpeg_binary(self, binary_name: str) -> Optional[str]:
        """Find FFmpeg binary in PATH."""
        return shutil.which(binary_name)
    
    def validate_ffmpeg(self) -> FFmpegInfo:
        """Validate FFmpeg installation and capabilities."""
        ffmpeg_path = self.find_ffmpeg_binary("ffmpeg")
        ffprobe_path = self.find_ffmpeg_binary("ffprobe")
        
        if not ffmpeg_path:
            return FFmpegInfo(
                ffmpeg_available=False,
                ffmpeg_version=None,
                ffprobe_available=False,
                libass_support=False,
                subtitle_support=False,
                ffmpeg_path=None,
                error_message="FFmpeg not found in PATH"
            )
            
        self.ffmpeg_path = ffmpeg_path
        
        # Check FFmpeg version
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            ffmpeg_version = None
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                ffmpeg_version = version_line.split('ffmpeg version ')[-1].split(' ')[0]
        except Exception as e:
            return FFmpegInfo(
                ffmpeg_available=True,
                ffmpeg_version=None,
                ffprobe_available=ffprobe_path is not None,
                libass_support=False,
                subtitle_support=False,
                ffmpeg_path=ffmpeg_path,
                error_message=f"Failed to get FFmpeg version: {e}"
            )
            
        # Check libass and subtitle support
        libass_support = False
        subtitle_support = False
        
        try:
            # Check for libass by looking for ass subtitle support
            result = subprocess.run(
                [ffmpeg_path, "-filters"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                filters_output = result.stdout.lower()
                libass_support = "libass" in filters_output or "ass" in filters_output
                subtitle_support = "subtitles" in filters_output or "ass" in filters_output
        except Exception as e:
            logger.warning(f"Failed to check FFmpeg filters: {e}")
            
        return FFmpegInfo(
            ffmpeg_available=True,
            ffmpeg_version=ffmpeg_version,
            ffprobe_available=ffprobe_path is not None,
            libass_support=libass_support,
            subtitle_support=subtitle_support,
            ffmpeg_path=ffmpeg_path
        )


class CUDAValidator:
    """CUDA toolkit validation utility."""
    
    def validate_cuda(self) -> CUDAInfo:
        """Validate CUDA toolkit installation."""
        nvcc_path = shutil.which("nvcc")
        
        if not nvcc_path:
            return CUDAInfo(
                nvcc_available=False,
                nvcc_version=None,
                cuda_path=None,
                cuda_version=None,
                error_message="nvcc not found in PATH"
            )
            
        # Get CUDA version from nvcc
        try:
            result = subprocess.run(
                [nvcc_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                # Extract version from "Cuda compilation tools, release X.Y.Z, ..."
                cuda_version = None
                if "release" in version_line:
                    parts = version_line.split("release ")
                    if len(parts) > 1:
                        version_part = parts[1].split(",")[0]
                        cuda_version = version_part
                        
                # Try to find CUDA path
                cuda_path = None
                cuda_home = os.environ.get("CUDA_HOME") or os.environ.get("CUDA_PATH")
                if cuda_home:
                    cuda_path = cuda_home
                else:
                    # Try to find CUDA installation path
                    nvcc_dir = Path(nvcc_path).parent.parent
                    if (nvcc_dir / "version.txt").exists():
                        cuda_path = str(nvcc_dir)
                        
                return CUDAInfo(
                    nvcc_available=True,
                    nvcc_version=result.stdout.split('\n')[0],
                    cuda_path=cuda_path,
                    cuda_version=cuda_version
                )
            else:
                return CUDAInfo(
                    nvcc_available=True,
                    nvcc_version=None,
                    cuda_path=None,
                    cuda_version=None,
                    error_message="nvcc found but failed to get version"
                )
                
        except Exception as e:
            return CUDAInfo(
                nvcc_available=True,
                nvcc_version=None,
                cuda_path=None,
                cuda_version=None,
                error_message=f"Failed to validate CUDA: {e}"
            )


class SystemValidator:
    """System validation and configuration utility."""
    
    def __init__(self):
        self.gpu_detector = GPUDetector()
        self.ffmpeg_validator = FFMpegValidator()
        self.cuda_validator = CUDAValidator()
        
    def validate_system(self) -> SystemInfo:
        """Validate complete system configuration."""
        gpu_info = self.gpu_detector.detect_gpu_info()
        ffmpeg_info = self.ffmpeg_validator.validate_ffmpeg()
        cuda_info = self.cuda_validator.validate_cuda()
        
        # Determine if we should fallback to CPU
        fallback_to_cpu = not gpu_info.cuda_available
        
        return SystemInfo(
            platform=platform.system(),
            architecture=platform.machine(),
            python_version=sys.version,
            gpu_info=gpu_info,
            ffmpeg_info=ffmpeg_info,
            cuda_info=cuda_info,
            fallback_to_cpu=fallback_to_cpu
        )


# Global FastAPI app instance
app = FastAPI(
    title="MEXC EMA Bot API",
    description="FastAPI application with GPU/CUDA and FFmpeg support",
    version="1.0.0"
)

# Global validator instance
system_validator = SystemValidator()

# Global system info cache
_system_info: Optional[SystemInfo] = None


@app.on_event("startup")
async def startup_event():
    """FastAPI startup event with system validation."""
    global _system_info
    
    logger.info("Starting MEXC EMA Bot FastAPI application...")
    
    # Validate system configuration
    _system_info = system_validator.validate_system()
    
    # Log validation results
    if _system_info.gpu_info.cuda_available:
        logger.info(f"✅ CUDA available: {_system_info.gpu_info.cuda_version}")
        logger.info(f"✅ GPU detected: {_system_info.gpu_info.gpu_name}")
        if _system_info.gpu_info.gpu_memory_total:
            memory_gb = _system_info.gpu_info.gpu_memory_total / (1024**3)
            logger.info(f"✅ GPU memory: {memory_gb:.1f} GB")
    else:
        logger.warning("⚠️ CUDA not available, will fallback to CPU")
        
    if _system_info.ffmpeg_info.ffmpeg_available:
        logger.info(f"✅ FFmpeg available: {_system_info.ffmpeg_info.ffmpeg_version}")
        if _system_info.ffmpeg_info.libass_support:
            logger.info("✅ FFmpeg libass support: enabled")
        if _system_info.ffmpeg_info.subtitle_support:
            logger.info("✅ FFmpeg subtitle support: enabled")
    else:
        logger.error(f"❌ FFmpeg not available: {_system_info.ffmpeg_info.error_message}")
        
    if _system_info.cuda_info.nvcc_available:
        logger.info(f"✅ CUDA toolkit available: {_system_info.cuda_info.cuda_version}")
    else:
        logger.warning(f"⚠️ CUDA toolkit not available: {_system_info.cuda_info.error_message}")
        
    # Log final fallback decision
    if _system_info.fallback_to_cpu:
        logger.warning("🤖 System configured to fallback to CPU processing")
    else:
        logger.info("🚀 System configured for GPU acceleration")
        
    logger.info("FastAPI application startup completed")


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "MEXC EMA Bot FastAPI Application",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "healthy"}
    )


@app.get("/system/info", response_model=SystemInfo)
async def get_system_info():
    """Get comprehensive system information."""
    if _system_info is None:
        _system_info = system_validator.validate_system()
    return _system_info


@app.get("/system/gpu", response_model=GPUInfo)
async def get_gpu_info():
    """Get GPU information."""
    gpu_info = system_validator.gpu_detector.detect_gpu_info()
    return gpu_info


@app.get("/system/ffmpeg", response_model=FFmpegInfo)
async def get_ffmpeg_info():
    """Get FFmpeg information."""
    ffmpeg_info = system_validator.ffmpeg_validator.validate_ffmpeg()
    return ffmpeg_info


@app.get("/system/cuda", response_model=CUDAInfo)
async def get_cuda_info():
    """Get CUDA information."""
    cuda_info = system_validator.cuda_validator.validate_cuda()
    return cuda_info


@app.post("/system/validate")
async def validate_system():
    """Trigger system validation and return results."""
    global _system_info
    _system_info = system_validator.validate_system()
    
    # Check for critical issues
    issues = []
    if not _system_info.gpu_info.cuda_available:
        issues.append("CUDA not available")
    if not _system_info.ffmpeg_info.ffmpeg_available:
        issues.append("FFmpeg not available")
        
    if issues:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "validation_complete",
                "issues": issues,
                "system_info": _system_info.dict()
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "validation_success",
                "message": "All systems operational",
                "system_info": _system_info.dict()
            }
        )


def create_fastapi_app() -> FastAPI:
    """Create and configure FastAPI application."""
    return app


def should_use_gpu() -> bool:
    """Check if GPU should be used based on system capabilities."""
    if _system_info is None:
        _system_info = system_validator.validate_system()
    return not _system_info.fallback_to_cpu


def get_gpu_info_sync() -> GPUInfo:
    """Get GPU information synchronously."""
    return system_validator.gpu_detector.detect_gpu_info()


def validate_ffmpeg_sync() -> FFmpegInfo:
    """Validate FFmpeg synchronously."""
    return system_validator.ffmpeg_validator.validate_ffmpeg()


def validate_cuda_sync() -> CUDAInfo:
    """Validate CUDA synchronously."""
    return system_validator.cuda_validator.validate_cuda()