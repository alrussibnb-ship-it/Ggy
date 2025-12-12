"""Configuration management for the MEXC EMA bot."""

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import os


class BotConfig:
    """
    Configuration class for the MEXC EMA bot.

    Loads environment variables from .env file and provides them as class attributes.
    """

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration by loading from environment.

        Args:
            env_file: Path to .env file. If None, looks for .env in project root.
        """
        if env_file:
            load_dotenv(env_file)
        else:
            # Look for .env in current working directory or project root
            env_path = Path(".env")
            if env_path.exists():
                load_dotenv(env_path)
            else:
                # Try loading without specifying path (uses default behavior)
                load_dotenv()

        # MEXC API Configuration
        self.mexc_api_key: str = self._get_required_env("MEXC_API_KEY")
        self.mexc_secret: str = self._get_required_env("MEXC_SECRET")

        # Telegram Configuration
        self.telegram_bot_token: str = self._get_required_env("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id: str = self._get_required_env("TELEGRAM_CHAT_ID")

        # Trading Configuration
        self.default_symbol: str = self._get_required_env(
            "DEFAULT_SYMBOL", default="BTCUSDT"
        )
        self.interval: str = self._get_required_env("INTERVAL", default="1h")

        # EMA Configuration
        self.fast_ema: int = self._get_env_as_int("FAST_EMA", default=12)
        self.slow_ema: int = self._get_env_as_int("SLOW_EMA", default=26)

        # MEXC Client Configuration
        self.mexc_base_url: str = self._get_required_env(
            "MEXC_BASE_URL", default="https://api.mexc.com"
        )
        self.kline_limit: int = self._get_env_as_int("KLINE_LIMIT", default=100)
        self.poll_interval: int = self._get_env_as_int("POLL_INTERVAL", default=60)
        self.max_retries: int = self._get_env_as_int("MAX_RETRIES", default=3)
        self.retry_delay: int = self._get_env_as_int("RETRY_DELAY", default=5)
        self.request_timeout: int = self._get_env_as_int("REQUEST_TIMEOUT", default=30)

        # Logging Configuration
        self.log_level: str = self._get_required_env("LOG_LEVEL", default="INFO")
        self.log_file: Optional[str] = os.getenv("LOG_FILE")

    @staticmethod
    def _get_required_env(key: str, default: Optional[str] = None) -> str:
        """
        Get a required environment variable.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Environment variable value

        Raises:
            ValueError: If required variable is missing and no default provided
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    @staticmethod
    def _get_env_as_int(key: str, default: Optional[int] = None) -> int:
        """
        Get an environment variable as an integer.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Integer value

        Raises:
            ValueError: If value cannot be converted to integer
        """
        value = os.getenv(key)
        if value is None:
            if default is None:
                raise ValueError(f"Required environment variable '{key}' is not set")
            return default

        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Environment variable '{key}' must be an integer, got: {value}")

    @staticmethod
    def _get_env_as_float(key: str, default: Optional[float] = None) -> float:
        """
        Get an environment variable as a float.

        Args:
            key: Environment variable name
            default: Default value if not found

        Returns:
            Float value

        Raises:
            ValueError: If value cannot be converted to float
        """
        value = os.getenv(key)
        if value is None:
            if default is None:
                raise ValueError(f"Required environment variable '{key}' is not set")
            return default

        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Environment variable '{key}' must be a float, got: {value}")

    def __repr__(self) -> str:
        """Return string representation of config (without sensitive data)."""
        return (
            f"BotConfig("
            f"symbol={self.default_symbol}, "
            f"interval={self.interval}, "
            f"fast_ema={self.fast_ema}, "
            f"slow_ema={self.slow_ema}"
            f")"
        )
