# MEXC EMA Bot

An automated trading bot for the MEXC exchange using Exponential Moving Average (EMA) indicators.

## Features

- Automated trading based on EMA crossover signals
- Real-time market data from MEXC exchange
- Telegram notifications for trading signals
- Configurable EMA periods (fast and slow)
- Centralized logging with configurable levels
- Graceful shutdown handling

## Requirements

- Python 3.8+
- pip (Python package manager)

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
- `INTERVAL` - Candle interval (e.g., 1h, 4h, 1d)
- `FAST_EMA` - Fast EMA period (default: 12)
- `SLOW_EMA` - Slow EMA period (default: 26)
- `LOG_LEVEL` - Logging level (default: INFO)

## Usage

### Run the bot

```bash
# Using make
make run

# Using the run script
./run.sh

# Using python directly (with PYTHONPATH set)
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python -m bot.main
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
│       └── logger.py            # Logging setup
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

## Signal Handling

The bot gracefully handles shutdown signals:
- `SIGINT` (Ctrl+C) - Stops the bot
- `SIGTERM` - Stops the bot

## Logging

Log messages are output to console and optionally to a file. The log level can be configured via the `LOG_LEVEL` environment variable.

Example log file location: `logs/bot.log` (when enabled via `LOG_FILE` environment variable)

## Future Implementation

The following features are marked for implementation:
- MEXC API connection and data streaming
- EMA indicator calculation
- Signal generation and trading logic
- Telegram notification system
- Order placement and management

## License

[Add your license information here]

## Support

[Add support information here]
