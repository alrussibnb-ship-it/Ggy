#!/usr/bin/env python3
"""
Simple bootstrap test to verify the project structure and basic imports.
This test can be run to verify that all modules are properly structured.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing module imports...")

    # Test logger module
    from bot.logger import setup_logger, get_logger
    print("✓ bot.logger imported successfully")

    # Test config module
    from bot.config import BotConfig
    print("✓ bot.config imported successfully")

    # Test main module
    from bot.main import MexcEmaBot, main
    print("✓ bot.main imported successfully")

    # Test package init
    from bot import __version__
    print(f"✓ bot package imported successfully (version: {__version__})")

    return True


def test_logger_setup():
    """Test logger setup functionality."""
    print("\nTesting logger setup...")

    from bot.logger import setup_logger

    logger = setup_logger("test_logger", level="DEBUG")
    logger.info("Test log message")
    print("✓ Logger setup and basic logging works")

    return True


def test_config_validation():
    """Test config validation."""
    print("\nTesting config validation...")

    from bot.config import BotConfig

    # Test that missing required env vars raise error
    try:
        config = BotConfig()
        print("✗ Config should have raised ValueError for missing env vars")
        return False
    except ValueError as e:
        print(f"✓ Config validation works: {e}")
        return True


def main_test():
    """Run all tests."""
    print("=" * 60)
    print("MEXC EMA Bot - Bootstrap Test")
    print("=" * 60)

    try:
        test_imports()
        test_logger_setup()
        test_config_validation()

        print("\n" + "=" * 60)
        print("✓ All bootstrap tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main_test())
