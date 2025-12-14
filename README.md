# Dual-Stack Audio Processing Application

A full-stack application for audio/video transcription and translation, featuring FastAPI backend, Celery workers, and Next.js frontend.

## 🚀 Features

- **Audio/Video Transcription**: Powered by faster-whisper for high-quality speech-to-text
- **Multi-language Translation**: Support for multiple translation providers (Google Translate, Transformers)
- **Subtitle Generation**: Create SRT and WebVTT subtitle files
- **Real-time Task Processing**: Asynchronous processing with Celery and Redis
- **Modern Web Interface**: Clean, responsive UI built with Next.js and Tailwind CSS
- **Docker Support**: Complete containerization for easy deployment
- **GPU Acceleration**: Optional GPU support for faster processing

## 🏗️ Architecture

```
├── backend/              # FastAPI application
│   ├── api/routes/       # API endpoints
│   ├── core/            # Core configuration
│   ├── workers/         # Celery workers
│   └── main.py          # FastAPI app entry point
├── frontend/            # Next.js application
│   ├── pages/           # Next.js pages
│   ├── components/      # React components
│   └── utils/           # Utility functions
├── storage/             # File storage directories
│   ├── uploads/         # User uploaded files
│   ├── media/           # Permanent media storage
│   └── outputs/         # Processing outputs
├── docker-compose.yml   # Multi-service Docker setup
├── .env.example         # Environment configuration
└── Makefile            # Development commands
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Celery** - Distributed task queue
- **Redis** - Message broker and result backend
- **faster-whisper** - Speech recognition
- **FFmpeg** - Audio/video processing
- **SRT** - Subtitle processing

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Hooks** - State management

## 📦 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (via Docker or native installation)
- FFmpeg (system installation)

### Option 1: Using Make (Recommended)

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd dual-stack-repo
   make install
   ```

2. **Start development servers**:
   ```bash
   make dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Option 2: Manual Setup

1. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   ```

3. **Start Redis** (Docker):
   ```bash
   docker run -d --name redis -p 6379:6379 redis:7-alpine
   ```

4. **Start services**:
   ```bash
   # Terminal 1: Backend
   cd backend && python -m uvicorn main:app --reload
   
   # Terminal 2: Celery Worker
   cd backend && celery -A core.celery_app worker --loglevel=info
   
   # Terminal 3: Frontend
   cd frontend && npm run dev
   ```

### Option 3: Docker Compose

```bash
docker-compose up -d
```

This starts all services:
- Redis on port 6379
- Backend on port 8000
- Frontend on port 3000
- Celery worker and beat scheduler

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key configuration options:

#### Backend Settings
- `REDIS_URL` - Redis connection URL
- `WHISPER_MODEL_SIZE` - Whisper model size (tiny, base, small, medium, large)
- `WHISPER_DEVICE` - Processing device (cpu, cuda)
- `TRANSLATION_PROVIDER` - Translation service (googletrans, transformers)

#### Frontend Settings
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_MAX_FILE_SIZE` - Maximum upload file size

See `.env.example` for all available options.

### Storage Configuration

The application uses three main storage directories:
- `storage/uploads/` - Temporary upload storage
- `storage/media/` - Permanent media storage
- `storage/outputs/` - Processing results and subtitles

## 🎯 Usage

### Web Interface

1. **Upload Files**: Drag and drop or select audio/video files
2. **Configure Processing**: Choose source and target languages
3. **Monitor Progress**: Real-time task status updates
4. **Download Results**: Access transcriptions and subtitles

### API Usage

#### Upload and Process File
```python
import requests

# Upload file
with open('audio.mp3', 'rb') as f:
    files = {'file': f}
    data = {'language': 'en', 'translate_to': 'es'}
    response = requests.post('http://localhost:8000/api/v1/files/upload', 
                           files=files, data=data)
    task_id = response.json()['task_id']

# Check status
status_response = requests.get(f'http://localhost:8000/api/v1/tasks/status/{task_id}')
print(status_response.json())
```

#### Health Checks
```python
# Basic health check
response = requests.get('http://localhost:8000/api/v1/health/')

# Detailed health check with dependencies
response = requests.get('http://localhost:8000/api/v1/health/detailed')
```

## 🔧 Development

### Available Make Commands

```bash
make help              # Show all available commands
make setup-env         # Create environment files
make install           # Install all dependencies
make dev               # Start development servers
make test              # Run all tests
make lint              # Run linting
make format            # Format code
make docker-up         # Start with Docker Compose
make clean             # Clean up generated files
```

### Project Structure

#### Backend (`backend/`)
- `main.py` - FastAPI application entry point
- `api/routes/` - API endpoints (files, tasks, health)
- `core/` - Configuration and Celery setup
- `workers/` - Background processing tasks

#### Frontend (`frontend/`)
- `pages/` - Next.js pages and API routes
- `components/` - React components
- `utils/` - API utilities and helpers

### Adding New Features

1. **Backend**: Add new routes in `backend/api/routes/`
2. **Workers**: Create new tasks in `backend/workers/`
3. **Frontend**: Add components in `frontend/components/`
4. **Storage**: Extend storage management in `backend/core/storage.py`

## 🐳 Docker Deployment

### Development
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Services
- **Redis**: Message broker and caching
- **Backend**: FastAPI application
- **Celery Worker**: Background task processor
- **Frontend**: Next.js web interface

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Backend Tests
```bash
cd backend && python -m pytest
```

### Frontend Tests
```bash
cd frontend && npm test
```

## 📝 API Documentation

When running the backend locally, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Files
- `POST /api/v1/files/upload` - Upload audio/video file
- `GET /api/v1/files/list` - List uploaded files
- `DELETE /api/v1/files/{file_id}` - Delete file

#### Tasks
- `GET /api/v1/tasks/status/{task_id}` - Check task status
- `POST /api/v1/tasks/cancel/{task_id}` - Cancel running task
- `GET /api/v1/tasks/active` - List active tasks

#### Health
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/detailed` - Detailed system status

## 🔧 Troubleshooting

### Redis Connection Issues

**Windows**: Use WSL or Docker
```bash
# WSL
sudo service redis-server start

# Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

**macOS**:
```bash
brew install redis
brew services start redis
```

**Linux**:
```bash
sudo apt install redis-server  # Ubuntu/Debian
sudo systemctl start redis     # Systemd systems
```

### FFmpeg Installation

**Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
**macOS**: `brew install ffmpeg`
**Linux**: `sudo apt install ffmpeg`

### GPU Support

To enable GPU acceleration for Whisper:

1. Install CUDA-compatible drivers
2. Set environment variables:
   ```bash
   export ENABLE_GPU=true
   export CUDA_VISIBLE_DEVICES=0
   export WHISPER_DEVICE=cuda
   ```

### Common Issues

**Port already in use**:
```bash
# Find process using port
lsof -i :8000
# Kill process
kill -9 <PID>
```

**Permission errors on storage directories**:
```bash
chmod -R 755 storage/
```

**Redis connection refused**:
```bash
# Check Redis status
redis-cli ping
# Restart Redis service
make redis-stop && make redis-start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run linting and tests (`make lint test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [faster-whisper](https://github.com/guillaumekln/faster-whisper) for speech recognition
- [FastAPI](https://fastapi.tiangolo.com/) for the modern Python web framework
- [Next.js](https://nextjs.org/) for the React framework
- [Celery](https://celeryproject.org/) for distributed task processing
- [Redis](https://redis.io/) for the message broker