.PHONY: help install install-dev run test lint format clean

help:
	@echo "MEXC EMA Bot - Available commands:"
	@echo ""
	@echo "  install           Install production dependencies"
	@echo "  install-dev       Install development dependencies"
	@echo "  run              Run the bot (requires .env file)"
	@echo "  test             Run tests"
	@echo "  lint             Run linting checks (flake8)"
	@echo "  format           Format code with black and isort"
	@echo "  clean            Remove cache and build artifacts"
	@echo "  setup-env        Create .env file from .env.example"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt

run:
	python -m bot.main

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
