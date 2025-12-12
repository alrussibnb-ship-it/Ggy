"""Main entry point for the MEXC EMA bot."""

import signal
import sys
from typing import Optional

from bot.config import BotConfig
from bot.logger import setup_logger, get_logger


logger = setup_logger(__name__)


class MexcEmaBot:
    """Main bot class for MEXC EMA trading bot."""

    def __init__(self, config: BotConfig):
        """
        Initialize the bot.

        Args:
            config: Bot configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self._running = False

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, frame: Optional[object]) -> None:
        """
        Handle shutdown signals gracefully.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.shutdown()

    def run(self) -> None:
        """
        Start the bot's main loop.

        This is the main entry point for bot execution.
        """
        try:
            self._running = True
            self.logger.info("Starting MEXC EMA Bot...")
            self.logger.info(f"Configuration: {self.config}")
            self.logger.info(
                f"Trading pair: {self.config.default_symbol} with interval {self.config.interval}"
            )
            self.logger.info(
                f"EMA settings: Fast={self.config.fast_ema}, Slow={self.config.slow_ema}"
            )

            # TODO: Implement main bot logic
            # - Connect to MEXC API
            # - Subscribe to market data
            # - Calculate EMA indicators
            # - Send signals via Telegram
            # - Place trades

            self.logger.info("Bot is running. Press Ctrl+C to stop.")

            # Keep the bot running
            while self._running:
                try:
                    # Placeholder for main loop logic
                    import time
                    time.sleep(1)
                except KeyboardInterrupt:
                    break

        except ValueError as e:
            self.logger.error(f"Configuration error: {e}", exc_info=True)
            sys.exit(1)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            sys.exit(1)

    def shutdown(self) -> None:
        """
        Gracefully shut down the bot.

        Closes connections, saves state, and cleanly exits.
        """
        if not self._running:
            return

        self._running = False
        self.logger.info("Shutting down bot...")

        try:
            # TODO: Implement cleanup logic
            # - Close API connections
            # - Save any pending state
            # - Cancel pending orders (if any)

            self.logger.info("Bot shutdown complete.")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}", exc_info=True)
            sys.exit(1)


def main() -> None:
    """Main entry point for the application."""
    try:
        # Load configuration
        config = BotConfig()

        # Set up logging with configured level
        setup_logger("bot", level=config.log_level, log_file=config.log_file)
        logger.info(f"Logging configured at level: {config.log_level}")

        # Create and run bot
        bot = MexcEmaBot(config)
        bot.run()

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
