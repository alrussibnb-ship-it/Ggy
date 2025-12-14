"""Test script for FastAPI application with GPU/CUDA/FFmpeg validation."""

import asyncio
import sys
import os
import platform
import subprocess
import shutil
from pathlib import Path


def test_system_info():
    """Test basic system information without heavy dependencies."""
    print("🖥️  System Information Test")
    print("=" * 50)
    
    print(f"Platform: {platform.system()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python Version: {sys.version.split()[0]}")
    print()


def test_path_validation():
    """Test PATH validation for FFmpeg and CUDA."""
    print("🔍 PATH Validation Test")
    print("=" * 50)
    
    # Test FFmpeg
    print("🎬 FFmpeg Detection:")
    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    
    if ffmpeg_path:
        print(f"✅ FFmpeg found: {ffmpeg_path}")
        try:
            result = subprocess.run([ffmpeg_path, "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ FFmpeg version: {version_line}")
            else:
                print("⚠️ FFmpeg found but version check failed")
        except Exception as e:
            print(f"⚠️ FFmpeg version check failed: {e}")
    else:
        print("❌ FFmpeg not found in PATH")
    
    if ffprobe_path:
        print(f"✅ FFprobe found: {ffprobe_path}")
    else:
        print("❌ FFprobe not found in PATH")
    
    # Test CUDA/nvcc
    print("\n⚡ CUDA Detection:")
    nvcc_path = shutil.which("nvcc")
    
    if nvcc_path:
        print(f"✅ NVCC found: {nvcc_path}")
        try:
            result = subprocess.run([nvcc_path, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ NVCC version: {version_line}")
            else:
                print("⚠️ NVCC found but version check failed")
        except Exception as e:
            print(f"⚠️ NVCC version check failed: {e}")
    else:
        print("❌ NVCC not found in PATH")
    
    # Test CUDA environment variables
    cuda_path = os.environ.get("CUDA_HOME") or os.environ.get("CUDA_PATH")
    if cuda_path:
        print(f"✅ CUDA_PATH/CUDA_HOME: {cuda_path}")
    else:
        print("⚠️ CUDA_PATH/CUDA_HOME not set")
    
    print()


def test_ffmpeg_filters():
    """Test FFmpeg filters for libass support."""
    print("🎭 FFmpeg Filters Test")
    print("=" * 50)
    
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        print("❌ FFmpeg not available for filter testing")
        return
    
    try:
        result = subprocess.run([ffmpeg_path, "-filters"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            filters_output = result.stdout.lower()
            
            # Check for libass and subtitle support
            libass_support = "libass" in filters_output or "ass" in filters_output
            subtitle_support = "subtitles" in filters_output or "ass" in filters_output
            
            print(f"Libass Support: {'✅ Yes' if libass_support else '❌ No'}")
            print(f"Subtitle Support: {'✅ Yes' if subtitle_support else '❌ No'}")
            
            if libass_support:
                print("✅ FFmpeg has libass support for subtitle rendering")
            else:
                print("⚠️ FFmpeg may lack libass support")
                
            if subtitle_support:
                print("✅ FFmpeg has subtitle filter support")
            else:
                print("⚠️ FFmpeg may lack subtitle filter support")
        else:
            print("⚠️ FFmpeg filters command failed")
    except Exception as e:
        print(f"❌ FFmpeg filter test failed: {e}")
    
    print()


def test_torch_availability():
    """Test PyTorch availability for CUDA detection."""
    print("🔥 PyTorch Availability Test")
    print("=" * 50)
    
    try:
        import torch
        print(f"✅ PyTorch version: {torch.__version__}")
        
        # Test CUDA availability
        cuda_available = torch.cuda.is_available()
        print(f"CUDA Available: {'✅ Yes' if cuda_available else '❌ No'}")
        
        if cuda_available:
            cuda_version = torch.version.cuda
            print(f"CUDA Version: {cuda_version}")
            
            gpu_count = torch.cuda.device_count()
            print(f"GPU Count: {gpu_count}")
            
            if gpu_count > 0:
                gpu_name = torch.cuda.get_device_name(0)
                print(f"GPU Name: {gpu_name}")
                
                # Get GPU memory if available
                if hasattr(torch.cuda, 'get_device_properties'):
                    props = torch.cuda.get_device_properties(0)
                    memory_gb = props.total_memory / (1024**3)
                    print(f"GPU Memory: {memory_gb:.1f} GB")
        else:
            print("ℹ️  PyTorch available but CUDA not available")
            
    except ImportError:
        print("❌ PyTorch not available - install with: pip install torch")
        print("💡 For CUDA support, install PyTorch with CUDA:")
        print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    except Exception as e:
        print(f"❌ PyTorch test failed: {e}")
    
    print()


def test_fastapi_availability():
    """Test FastAPI availability."""
    print("🚀 FastAPI Availability Test")
    print("=" * 50)
    
    try:
        import fastapi
        print(f"✅ FastAPI version: {fastapi.__version__}")
        
        import uvicorn
        print(f"✅ Uvicorn available")
        
        print("ℹ️  FastAPI application can be started with:")
        print("   python -m bot.fastapi_main")
        print("   or")
        print("   make fastapi")
        
    except ImportError:
        print("❌ FastAPI not available - install with: pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
    
    print()


def test_python_imports():
    """Test basic Python module imports."""
    print("📦 Python Module Import Test")
    print("=" * 50)
    
    # Test basic modules
    basic_modules = [
        ("sys", "System module"),
        ("os", "Operating system module"),
        ("platform", "Platform information"),
        ("subprocess", "Subprocess module"),
        ("shutil", "Shell utilities"),
        ("json", "JSON module"),
    ]
    
    for module_name, description in basic_modules:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name})")
        except ImportError:
            print(f"❌ {description} ({module_name}) - import failed")
    
    # Test optional modules
    optional_modules = [
        ("torch", "PyTorch (for GPU support)"),
        ("fastapi", "FastAPI (for web interface)"),
        ("uvicorn", "Uvicorn (for FastAPI server)"),
        ("requests", "HTTP requests"),
        ("httpx", "HTTP client"),
    ]
    
    print("\nOptional modules:")
    for module_name, description in optional_modules:
        try:
            __import__(module_name)
            print(f"✅ {description} ({module_name})")
        except ImportError:
            print(f"⚠️  {description} ({module_name}) - not available")


def main():
    """Main test function."""
    print("🧪 MEXC EMA Bot - GPU/CUDA/FFmpeg System Validation Test")
    print("=" * 70)
    print("Note: This test checks system capabilities without requiring all dependencies")
    print()
    
    # Test basic system info
    test_system_info()
    
    # Test PATH validation
    test_path_validation()
    
    # Test FFmpeg filters
    test_ffmpeg_filters()
    
    # Test PyTorch availability
    test_torch_availability()
    
    # Test FastAPI availability
    test_fastapi_availability()
    
    # Test Python imports
    test_python_imports()
    
    print("✅ System validation test completed")
    print("\n📋 Next Steps:")
    print("1. Install required dependencies: make install")
    print("2. Set up environment variables: copy .env.example to .env")
    print("3. Configure GPU drivers and CUDA toolkit")
    print("4. Install FFmpeg with libass support")
    print("5. Run full validation: make test-system")
    print("6. Start FastAPI server: make fastapi")
    print("\n📖 See GPU_FFMPEG_SETUP.md for detailed setup instructions")


if __name__ == "__main__":
    main()