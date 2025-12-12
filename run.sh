#!/bin/bash

# Run script for MEXC EMA Bot
# Usage: ./run.sh [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file by copying .env.example:"
    echo "  cp .env.example .env"
    echo ""
    echo "Then update .env with your actual credentials."
    exit 1
fi

# Check if PYTHONPATH is set to include src directory
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}${SCRIPT_DIR}/src"

# Run the bot
python -m bot.main "$@"
