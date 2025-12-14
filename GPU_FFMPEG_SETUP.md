# GPU, CUDA & FFmpeg Configuration Guide

## Overview

The MEXC EMA Bot now includes comprehensive GPU acceleration support via NVIDIA CUDA, FFmpeg with libass subtitle support, and a FastAPI web interface. The system automatically detects available hardware and software capabilities, with intelligent fallback to CPU processing when GPU is not available.

## Key Features

- ✅ **GPU Acceleration**: Automatic CUDA detection and utilization
- ✅ **FFmpeg Support**: Native FFmpeg with libass and subtitle capabilities
- ✅ **FastAPI Interface**: Web-based API for system monitoring and control
- ✅ **Intelligent Fallback**: Automatic CPU fallback when GPU unavailable
- ✅ **Windows Support**: Full Windows compatibility with CUDA toolkit
- ✅ **System Validation**: Comprehensive hardware/software validation

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- Internet connection for dependencies

### GPU Acceleration Requirements
- NVIDIA GPU with CUDA Compute Capability 6.1+
- NVIDIA CUDA Toolkit 11.0+
- NVIDIA GPU drivers (latest recommended)

### FFmpeg Requirements
- FFmpeg with libass support
- Windows: Native Windows build or WSL
- Linux: Package manager installation

## Installation

### 1. Install Dependencies

```bash
# Clone repository
git clone <repository-url>
cd mexc-ema-bot

# Install dependencies
make install

# Or manually with pip
pip install -r requirements.txt
```

### 2. Windows CUDA Setup

#### Option A: Install NVIDIA CUDA Toolkit
1. Download CUDA Toolkit from [NVIDIA Developer](https://developer.nvidia.com/cuda-downloads)
2. Run installer with default options
3. Verify installation:
   ```cmd
   nvcc --version
   nvidia-smi
   ```

#### Option B: Verify Environment Variables
Ensure these environment variables are set:
```
CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x
CUDA_HOME=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x
PATH includes: C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.x\bin
```

### 3. FFmpeg Installation

#### Windows Options

**Option A: Native Windows Build**
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   ```
   C:\ffmpeg\bin
   ```

**Option B: Using Chocolatey**
```cmd
choco install ffmpeg
```

**Option C: Using WSL (Recommended for development)**
```bash
sudo apt update
sudo apt install ffmpeg libass-dev
```

#### Linux Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg libass-dev

# CentOS/RHEL
sudo yum install ffmpeg libass-devel

# Arch Linux
sudo pacman -S ffmpeg libass
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required MEXC API Configuration
MEXC_API_KEY=your_api_key_here
MEXC_SECRET=your_secret_here

# Required Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# GPU/CUDA Configuration
GPU_ENABLED=true              # Enable GPU support (true/false)
CUDA_DEVICE=0                 # CUDA device index (0 = first GPU)
FORCE_CPU=false               # Force CPU even if GPU available (true/false)

# FFmpeg Configuration
# FFMPEG_PATH=/usr/bin/ffmpeg    # Custom FFmpeg path (optional)
# FFPROBE_PATH=/usr/bin/ffprobe  # Custom FFprobe path (optional)
FFMPEG_TIMEOUT=30             # FFmpeg command timeout

# FastAPI Configuration
FASTAPI_HOST=127.0.0.1        # Web interface host
FASTAPI_PORT=8000             # Web interface port
FASTAPI_RELOAD=false          # Enable auto-reload for development

# System Configuration
ENABLE_GPU_MONITORING=true    # Enable GPU monitoring
GPU_MEMORY_FRACTION=0.8       # GPU memory usage limit (0.0-1.0)
```

### Configuration Priorities

1. **GPU Detection**: Automatically detects CUDA-capable GPUs
2. **Manual Override**: `FORCE_CPU=true` disables GPU even if available
3. **Device Selection**: `CUDA_DEVICE` selects specific GPU
4. **Memory Management**: `GPU_MEMORY_fraction` controls memory usage

## Usage

### Starting the Bot

#### Command Line Interface
```bash
# Start bot with system validation
make run

# Or directly
python -m bot.main
```

#### FastAPI Web Interface
```bash
# Start FastAPI server
python -m bot.fastapi_main

# Access web interface
open http://localhost:8000
```

### API Endpoints

#### System Information
```bash
# Get comprehensive system info
curl http://localhost:8000/system/info

# Get GPU information only
curl http://localhost:8000/system/gpu

# Get FFmpeg information only
curl http://localhost:8000/system/ffmpeg

# Get CUDA information only
curl http://localhost:8000/system/cuda

# Trigger system validation
curl -X POST http://localhost:8000/system/validate
```

#### Health Check
```bash
# Basic health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

### Python Integration

```python
from bot.fastapi_app import (
    should_use_gpu, 
    get_gpu_info_sync, 
    validate_ffmpeg_sync,
    SystemValidator
)

# Check if GPU should be used
if should_use_gpu():
    print("Using GPU acceleration")
else:
    print("Using CPU fallback")

# Get GPU information
gpu_info = get_gpu_info_sync()
print(f"CUDA Available: {gpu_info.cuda_available}")
print(f"GPU Name: {gpu_info.gpu_name}")

# Validate FFmpeg
ffmpeg_info = validate_ffmpeg_sync()
print(f"FFmpeg Version: {ffmpeg_info.ffmpeg_version}")

# Full system validation
validator = SystemValidator()
system_info = validator.validate_system()
print(f"Fallback to CPU: {system_info.fallback_to_cpu}")
```

## Fallback Mechanisms

### GPU Fallback Logic

1. **Detect CUDA**: Check `torch.cuda.is_available()`
2. **Validate GPU**: Check for NVIDIA GPU with sufficient memory
3. **Configuration Check**: Respect `GPU_ENABLED` and `FORCE_CPU` settings
4. **Memory Check**: Verify available GPU memory
5. **Fallback Decision**: Use CPU if any validation fails

### FFmpeg Fallback Logic

1. **Binary Detection**: Find `ffmpeg` in PATH or custom path
2. **Version Check**: Verify FFmpeg version
3. **Filter Validation**: Check for libass and subtitle filters
4. **Graceful Degradation**: Continue without FFmpeg if not available

### Error Handling

- **Missing GPU**: Automatic CPU fallback with warning
- **Missing FFmpeg**: Operations continue without media processing
- **Invalid Configuration**: Use sensible defaults
- **Timeout Errors**: Continue with available resources

## Windows-Specific Notes

### CUDA on Windows

1. **Installation**: Use official NVIDIA installer
2. **Environment Variables**: Automatically set by CUDA installer
3. **Verification**: Use `nvcc --version` and `nvidia-smi`
4. **Path Resolution**: Tool finds CUDA automatically

### FFmpeg on Windows

1. **Native Builds**: Recommended for production
2. **WSL Option**: Good for development
3. **Path Configuration**: Use `FFMPEG_PATH` for custom locations
4. **Binary Naming**: Ensure `ffmpeg.exe` and `ffprobe.exe` are accessible

## Troubleshooting

### GPU Issues

#### CUDA Not Available
```
❌ CUDA not available, will fallback to CPU
```
**Solution**: Install NVIDIA drivers and CUDA toolkit

#### GPU Memory Issues
```
⚠️ GPU memory limit: 0.8 (80%)
```
**Solution**: Adjust `GPU_MEMORY_FRACTION` or use smaller batch sizes

#### Multiple GPUs
```
CUDA device: 0
```
**Solution**: Set `CUDA_DEVICE` to select specific GPU

### FFmpeg Issues

#### FFmpeg Not Found
```
❌ FFmpeg not available: FFmpeg not found in PATH
```
**Solution**: Install FFmpeg or set `FFMPEG_PATH`

#### Missing Libass
```
FFmpeg libass support: disabled
```
**Solution**: Reinstall FFmpeg with libass support

### FastAPI Issues

#### Port Already in Use
```
Address already in use
```
**Solution**: Change `FASTAPI_PORT` or stop conflicting process

#### Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: Install dependencies with `make install`

### Performance Optimization

#### GPU Utilization
```python
# Check GPU utilization
gpu_info = get_gpu_info_sync()
if gpu_info.gpu_utilization > 90:
    print("GPU heavily loaded, consider CPU fallback")
```

#### Memory Management
```python
# Monitor GPU memory
if gpu_info.gpu_memory_used / gpu_info.gpu_memory_total > 0.9:
    print("GPU memory nearly full")
```

## Advanced Configuration

### Custom CUDA Paths

```bash
# Set custom CUDA installation path
export CUDA_HOME=/path/to/custom/cuda
export PATH=$CUDA_HOME/bin:$PATH
```

### Custom FFmpeg Configuration

```bash
# Use custom FFmpeg binary
FFMPEG_PATH=/opt/custom/ffmpeg/bin/ffmpeg
FFPROBE_PATH=/opt/custom/ffmpeg/bin/ffprobe
```

### GPU Memory Optimization

```python
# Limit GPU memory usage
import torch
torch.cuda.set_per_process_memory_fraction(0.8, device=0)
```

### Monitoring and Logging

The system provides comprehensive logging:

```bash
# Enable debug logging
LOG_LEVEL=DEBUG python -m bot.main

# Monitor GPU usage
curl http://localhost:8000/system/gpu
```

## Security Considerations

- API keys are loaded from environment variables
- FastAPI runs on localhost by default
- GPU credentials are not stored
- No sensitive data in logs

## Development

### Testing System Validation

```bash
# Run comprehensive test
python test_fastapi.py

# Test individual components
python -c "from bot.fastapi_app import SystemValidator; \
           print(validator.validate_system())"
```

### Debugging Configuration

```python
# Enable detailed logging
import logging
logging.getLogger('bot.fastapi_app').setLevel(logging.DEBUG)
```

## Support

For issues and questions:

1. Check this documentation
2. Run `test_fastapi.py` for diagnostics
3. Review API endpoint responses
4. Check system logs with `LOG_LEVEL=DEBUG`

## Version Compatibility

- Python 3.8+
- PyTorch 2.1.1+
- CUDA 11.0+
- FFmpeg 4.0+
- FastAPI 0.104.1+