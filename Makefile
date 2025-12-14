# Simple development Makefile for dual-stack application

.PHONY: help setup install dev redis-start redis-stop

help:
	@echo "Available commands:"
	@echo "  setup       - Setup environment files and directories"
	@echo "  install     - Install all dependencies"
	@echo "  dev-backend - Start backend development server"
	@echo "  dev-frontend- Start frontend development server"
	@echo "  redis-start - Start Redis server"
	@echo "  redis-stop  - Stop Redis server"

setup:
	@echo "Setting up environment..."
	@cp .env.example .env 2>/dev/null || true
	@cp frontend/.env.local.example frontend/.env.local 2>/dev/null || true
	@mkdir -p storage/uploads storage/media storage/outputs
	@echo "Setup complete!"

install: setup
	@echo "Installing dependencies..."
	@echo "Backend: pip install -r backend/requirements.txt"
	@echo "Frontend: npm install (in frontend directory)"

dev-backend:
	@echo "Starting backend server..."
	@cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev-frontend:
	@echo "Starting frontend server..."
	@cd frontend && npm run dev

redis-start:
	@echo "Starting Redis..."
	@docker run -d --name audio-processing-redis -p 6379:6379 redis:7-alpine || echo "Redis already running or Docker not available"

redis-stop:
	@echo "Stopping Redis..."
	@docker stop audio-processing-redis 2>/dev/null || true
	@docker rm audio-processing-redis 2>/dev/null || true
