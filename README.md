# MEXC EMA Bot

An automated trading bot for the MEXC exchange using Exponential Moving Average (EMA) indicators.

## Features

### Core Trading Features
- Automated trading based on EMA crossover signals
- Real-time market data from MEXC exchange
- Telegram notifications for trading signals
- Configurable EMA periods (fast and slow)
- Centralized logging with configurable levels
- Graceful shutdown handling

### GPU Acceleration & Media Processing
- **NVIDIA CUDA Support**: Automatic GPU detection and utilization
- **FFmpeg Integration**: Native FFmpeg with libass and subtitle support
- **Intelligent Fallback**: Automatic CPU fallback when GPU unavailable
- **System Validation**: Comprehensive hardware/software validation
- **Performance Monitoring**: Real-time GPU utilization tracking

### FastAPI Web Interface
- **REST API**: Full FastAPI application with multiple endpoints
- **System Monitoring**: GPU, CUDA, and FFmpeg status monitoring
- **Health Checks**: Application health and readiness endpoints
- **Configuration Validation**: Dynamic system configuration validation
- **Web-based Interface**: Browser-accessible system information

## Requirements

### Minimum Requirements
- Python 3.8+
- pip (Python package manager)
- 4GB RAM
- Internet connection

### GPU Acceleration (Optional)
- NVIDIA GPU with CUDA Compute Capability 6.1+
- NVIDIA CUDA Toolkit 11.0+
- NVIDIA GPU drivers

### FFmpeg Support (Optional)
- FFmpeg with libass support
- Windows: Native Windows build or WSL
- Linux: Package manager installation

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd mexc-ema-bot
```

### 2. Install dependencies

```bash
# Using make
make install

# Or directly with pip
pip install -r requirements.txt
```

### 3. Set up environment variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual credentials
# nano .env  # or your preferred editor
```

### Required environment variables:

- `MEXC_API_KEY` - Your MEXC API key
- `MEXC_SECRET` - Your MEXC API secret
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID
- `DEFAULT_SYMBOL` - Trading pair (e.g., BTCUSDT)
- `INTERVAL` - Candle interval (1m, 5m, 15m, 30m, 60m, 4h, 1d, 1w, 1M)
- `FAST_EMA` - Fast EMA period (default: 12)
- `SLOW_EMA` - Slow EMA period (default: 26)
- `LOG_LEVEL` - Logging level (default: INFO)

## Usage

### Run the Trading Bot

```bash
# Using make
make run

# Using the run script
./run.sh

# Using python directly (with PYTHONPATH set)
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m bot.main
```

### Run FastAPI Web Interface

```bash
# Start FastAPI server
make fastapi

# Or using python directly
python -m bot.fastapi_main

# Access web interface
open http://localhost:8000
```

### System Validation

```bash
# Run comprehensive system validation
make test-system

# Quick validation check
make validate

# GPU setup guide
make setup-gpu
```

## Development

### Install development dependencies

```bash
make install-dev
```

### Run tests

```bash
make test
```

### Format code

```bash
make format
```

### Run linting

```bash
make lint
```

### Clean up cache

```bash
make clean
```

## Project Structure

```
mexc-ema-bot/
├── src/
│   └── bot/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Main entry point for python -m bot
│       ├── main.py              # Main bot class and entry function
│       ├── config.py            # Configuration management
│       ├── logger.py            # Logging setup
│       └── mexc_client.py       # MEXC API client
├── tests/
│   └── test_mexc_client.py      # Unit tests for MEXC client
├── examples/
│   └── test_mexc_client.py      # Example usage of MEXC client
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
├── Makefile                     # Development commands
├── run.sh                       # Bash run script
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## Architecture

### Configuration (`config.py`)

Loads environment variables from `.env` file and provides them as class attributes. Includes validation for required variables.

### Logging (`logger.py`)

Centralized logging setup with support for:
- Console output with formatted messages
- Rotating file handlers (optional)
- Configurable log levels

### Main Bot (`main.py`)

Main bot class that:
- Initializes from configuration
- Handles graceful shutdown via signal handlers (SIGINT, SIGTERM)
- Provides a main execution loop
- Implements proper error handling

### MEXC Client (`mexc_client.py`)

Comprehensive client for interacting with MEXC REST API:

#### Features
- **Async HTTP Client**: Built on `httpx` for high-performance async operations
- **Kline Data Fetching**: Retrieve candlestick data for any trading pair and interval
- **Robust Error Handling**: 
  - Automatic retry with exponential backoff
  - Rate limit detection and handling
  - Network error recovery
- **Rate Limiting**: Respects MEXC API rate limits
- **Structured Logging**: Detailed logging of all operations and errors
- **Data Models**: Type-safe `KlineData` dataclass for candlestick data

#### Components

##### MexcClient
Main client class for API interactions:
- `get_klines()` - Fetch historical kline/candlestick data
- `get_latest_price()` - Get the latest close price for a symbol
- Configurable retry logic and timeouts
- Context manager support for proper resource cleanup

##### KlinePoller
Continuous polling loop for real-time data:
- Polls for new kline data at configurable intervals
- Invokes callback functions with new data
- Supports both sync and async callbacks
- Tracks latest data to avoid duplicate processing
- Graceful start/stop with proper cleanup

##### KlineData
Structured dataclass representing candlestick data:
- All OHLCV (Open, High, Low, Close, Volume) fields
- Timestamp conversion utilities
- Easy serialization to dict
- Type-safe construction from API responses

#### Usage Example

```python
from bot.mexc_client import MexcClient, KlinePoller

# Simple data fetch
async with MexcClient() as client:
    klines = await client.get_klines("BTCUSDT", "60m", limit=100)
    for kline in klines:
        print(f"{kline.close_time_dt}: {kline.close}")

# Continuous polling
def on_new_data(klines):
    latest = klines[-1]
    print(f"New price: {latest.close}")

async with MexcClient() as client:
    poller = KlinePoller(
        client=client,
        symbol="BTCUSDT",
        interval="60m",
        poll_interval=60,
        callback=on_new_data
    )
    await poller.start()
    # ... bot logic ...
    await poller.stop()
```

#### Configuration Options

The client supports the following configuration via environment variables:
- `MEXC_BASE_URL` - API base URL (default: https://api.mexc.com)
- `KLINE_LIMIT` - Number of klines per request (default: 100, max: 1000)
- `POLL_INTERVAL` - Seconds between polls (default: 60)
- `MAX_RETRIES` - Max retry attempts for failed requests (default: 3)
- `RETRY_DELAY` - Initial retry delay in seconds (default: 5)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: 30)

## Signal Handling

The bot gracefully handles shutdown signals:
- `SIGINT` (Ctrl+C) - Stops the bot
- `SIGTERM` - Stops the bot

## Logging

Log messages are output to console and optionally to a file. The log level can be configured via the `LOG_LEVEL` environment variable.

Example log file location: `logs/bot.log` (when enabled via `LOG_FILE` environment variable)

## Testing

### Run Unit Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_mexc_client.py -v

# Run with coverage
pytest --cov=bot tests/
```

### Run Examples

The `examples/` directory contains example scripts demonstrating client usage:

```bash
# Make sure .env is configured first
python examples/test_mexc_client.py
```

## Future Implementation

The following features are marked for implementation:
- ✅ MEXC API connection and data streaming
- EMA indicator calculation
- Signal generation and trading logic
- Telegram notification system
- Order placement and management

## License

[Add your license information here]

## Support

[Add support information here]
