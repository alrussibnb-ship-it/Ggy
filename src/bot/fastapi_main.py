"""FastAPI server entry point for MEXC EMA Bot."""

import uvicorn
from src.bot.fastapi_app import app
from src.bot.config import BotConfig
from src.bot.logger import get_logger

logger = get_logger(__name__)


def main():
    """Run the FastAPI server."""
    config = BotConfig()
    
    logger.info(f"Starting FastAPI server on {config.fastapi_host}:{config.fastapi_port}")
    logger.info(f"GPU enabled: {config.gpu_enabled}")
    logger.info(f"CUDA device: {config.cuda_device}")
    
    uvicorn.run(
        app,
        host=config.fastapi_host,
        port=config.fastapi_port,
        reload=config.fastapi_reload,
        log_level=config.log_level.lower()
    )


if __name__ == "__main__":
    main()