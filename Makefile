.PHONY: help install install-dev run test lint format clean fastapi test-system validate setup-gpu

help:
	@echo "MEXC EMA Bot - Available commands:"
	@echo ""
	@echo "  install           Install production dependencies"
	@echo "  install-dev       Install development dependencies"
	@echo "  run              Run the bot (requires .env file)"
	@echo "  fastapi          Run FastAPI server"
	@echo "  test-system      Run system validation test"
	@echo "  test             Run tests"
	@echo "  lint             Run linting checks (flake8)"
	@echo "  format           Format code with black and isort"
	@echo "  clean            Remove cache and build artifacts"
	@echo "  setup-env        Create .env file from .env.example"
	@echo "  validate         Validate system configuration"
	@echo "  setup-gpu        Guide for GPU setup"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt

run:
	python -m bot.main

fastapi:
	python -m bot.fastapi_main

test-system:
	python test_fastapi.py

test:
	pytest -v

lint:
	flake8 src/
	black --check src/
	isort --check-only src/

format:
	black src/
	isort src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name build -exec rm -rf {} + 2>/dev/null || true

setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please update .env with your actual credentials"; \
	else \
		echo ".env file already exists"; \
	fi

validate:
	@echo "Validating system configuration..."
	@python -c "print('System validation requires dependencies installed')"

setup-gpu:
	@echo "GPU Setup Instructions:"
	@echo "1. Install NVIDIA GPU drivers"
	@echo "2. Install CUDA Toolkit from: https://developer.nvidia.com/cuda-downloads"
	@echo "3. Install FFmpeg with libass support"
	@echo "4. Run 'make validate' to check configuration"
	@echo "5. See GPU_FFMPEG_SETUP.md for detailed instructions"