"""MEXC API client for fetching market data."""

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, List, Optional
from enum import Enum

import httpx

from bot.logger import get_logger


class KlineInterval(str, Enum):
    """Valid kline interval values for MEXC API."""
    
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    FOUR_HOURS = "4h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1M"


@dataclass
class KlineData:
    """
    Represents a single candlestick (kline) data point.
    
    Attributes:
        open_time: Opening time in milliseconds
        open: Opening price
        high: Highest price
        low: Lowest price
        close: Closing price
        volume: Trading volume
        close_time: Closing time in milliseconds
        quote_volume: Quote asset volume
        trades: Number of trades
        taker_buy_base_volume: Taker buy base asset volume
        taker_buy_quote_volume: Taker buy quote asset volume
    """
    
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int
    quote_volume: float
    trades: int
    taker_buy_base_volume: float
    taker_buy_quote_volume: float
    
    @classmethod
    def from_api_response(cls, data: List) -> "KlineData":
        """
        Create KlineData from MEXC API response array.
        
        Args:
            data: Array from MEXC API response
            
        Returns:
            KlineData instance
        """
        return cls(
            open_time=int(data[0]),
            open=float(data[1]),
            high=float(data[2]),
            low=float(data[3]),
            close=float(data[4]),
            volume=float(data[5]),
            close_time=int(data[6]),
            quote_volume=float(data[7]),
            trades=int(data[8]) if len(data) > 8 else 0,
            taker_buy_base_volume=float(data[9]) if len(data) > 9 else 0.0,
            taker_buy_quote_volume=float(data[10]) if len(data) > 10 else 0.0,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "open_time": self.open_time,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "close_time": self.close_time,
            "quote_volume": self.quote_volume,
            "trades": self.trades,
            "taker_buy_base_volume": self.taker_buy_base_volume,
            "taker_buy_quote_volume": self.taker_buy_quote_volume,
        }
    
    @property
    def open_time_dt(self) -> datetime:
        """Get opening time as datetime object."""
        return datetime.fromtimestamp(self.open_time / 1000)
    
    @property
    def close_time_dt(self) -> datetime:
        """Get closing time as datetime object."""
        return datetime.fromtimestamp(self.close_time / 1000)


class MexcClientError(Exception):
    """Base exception for MEXC client errors."""
    pass


class MexcAPIError(MexcClientError):
    """Exception raised when MEXC API returns an error."""
    
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"MEXC API Error {code}: {message}")


class MexcRateLimitError(MexcClientError):
    """Exception raised when rate limit is exceeded."""
    pass


class MexcClient:
    """
    Client for interacting with MEXC REST API.
    
    Provides methods for fetching market data with retry logic,
    rate limiting, and robust error handling.
    """
    
    KLINE_ENDPOINT = "/api/v3/klines"
    
    def __init__(
        self,
        base_url: str = "https://api.mexc.com",
        max_retries: int = 3,
        retry_delay: int = 5,
        request_timeout: int = 30,
    ):
        """
        Initialize MEXC client.
        
        Args:
            base_url: Base URL for MEXC API
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            request_timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.request_timeout = request_timeout
        self.logger = get_logger(__name__)
        self._client: Optional[httpx.AsyncClient] = None
        self._rate_limit_remaining = 1200
        self._rate_limit_reset = 0
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
        
    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.request_timeout,
                headers={
                    "User-Agent": "MEXC-EMA-Bot/1.0",
                    "Content-Type": "application/json",
                },
            )
    
    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        retry_count: int = 0,
    ) -> dict:
        """
        Make an HTTP request with retry logic and error handling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            retry_count: Current retry attempt number
            
        Returns:
            Response data as dictionary
            
        Raises:
            MexcAPIError: If API returns an error
            MexcRateLimitError: If rate limit is exceeded
            MexcClientError: For other client errors
        """
        await self._ensure_client()
        
        try:
            self.logger.debug(f"Making {method} request to {endpoint} with params: {params}")
            
            response = await self._client.request(method, endpoint, params=params)
            
            self._update_rate_limits(response)
            
            if response.status_code == 429:
                raise MexcRateLimitError("Rate limit exceeded")
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    code = error_data.get("code", response.status_code)
                    message = error_data.get("msg", response.text)
                    raise MexcAPIError(code, message)
                except (ValueError, KeyError):
                    raise MexcAPIError(response.status_code, response.text)
            
            response.raise_for_status()
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            
            return {"data": response.text}
            
        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
            self.logger.warning(
                f"Network error on attempt {retry_count + 1}/{self.max_retries}: {e}"
            )
            
            if retry_count < self.max_retries:
                delay = self.retry_delay * (2 ** retry_count)
                self.logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                return await self._make_request(method, endpoint, params, retry_count + 1)
            
            raise MexcClientError(f"Network error after {self.max_retries} retries: {e}")
        
        except MexcRateLimitError as e:
            self.logger.warning(f"Rate limit exceeded on attempt {retry_count + 1}")
            
            if retry_count < self.max_retries:
                delay = self._get_rate_limit_delay()
                self.logger.info(f"Waiting {delay} seconds for rate limit reset...")
                await asyncio.sleep(delay)
                return await self._make_request(method, endpoint, params, retry_count + 1)
            
            raise
        
        except MexcAPIError as e:
            self.logger.error(f"API error: {e}")
            
            if retry_count < self.max_retries and self._is_retryable_error(e.code):
                delay = self.retry_delay * (2 ** retry_count)
                self.logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                return await self._make_request(method, endpoint, params, retry_count + 1)
            
            raise
    
    def _update_rate_limits(self, response: httpx.Response):
        """Update rate limit information from response headers."""
        if "x-mbx-used-weight-1m" in response.headers:
            used_weight = int(response.headers["x-mbx-used-weight-1m"])
            self._rate_limit_remaining = max(0, 1200 - used_weight)
            self.logger.debug(f"Rate limit remaining: {self._rate_limit_remaining}")
    
    def _get_rate_limit_delay(self) -> int:
        """Calculate delay for rate limit reset."""
        if self._rate_limit_reset > time.time():
            return int(self._rate_limit_reset - time.time()) + 1
        return 60
    
    def _is_retryable_error(self, code: int) -> bool:
        """Check if an error code is retryable."""
        retryable_codes = {500, 502, 503, 504, -1001, -1021}
        return code in retryable_codes
    
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[KlineData]:
        """
        Fetch kline/candlestick data for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            interval: Kline interval (e.g., 1m, 5m, 1h, 1d)
            limit: Number of klines to fetch (max 1000, default 100)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            
        Returns:
            List of KlineData objects
            
        Raises:
            MexcClientError: If request fails
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, 1000),
        }
        
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        self.logger.info(
            f"Fetching klines for {symbol} with interval {interval}, limit {limit}"
        )
        
        try:
            response = await self._make_request("GET", self.KLINE_ENDPOINT, params)
            
            if not isinstance(response, list):
                raise MexcClientError(f"Unexpected response format: {type(response)}")
            
            klines = [KlineData.from_api_response(item) for item in response]
            
            self.logger.info(f"Successfully fetched {len(klines)} klines for {symbol}")
            
            if klines:
                self.logger.debug(
                    f"Latest kline: open_time={klines[-1].open_time_dt}, "
                    f"close={klines[-1].close}"
                )
            
            return klines
            
        except Exception as e:
            self.logger.error(f"Failed to fetch klines: {e}", exc_info=True)
            raise
    
    async def get_latest_price(self, symbol: str, interval: str) -> float:
        """
        Get the latest close price for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., BTCUSDT)
            interval: Kline interval (e.g., 1m, 5m, 1h, 1d)
            
        Returns:
            Latest close price
            
        Raises:
            MexcClientError: If request fails
        """
        klines = await self.get_klines(symbol, interval, limit=1)
        
        if not klines:
            raise MexcClientError(f"No klines returned for {symbol}")
        
        return klines[0].close


class KlinePoller:
    """
    Continuously polls for new kline data and feeds it to a callback.
    
    Implements a polling loop that fetches new market data at regular
    intervals and invokes a callback function with the latest data.
    """
    
    def __init__(
        self,
        client: MexcClient,
        symbol: str,
        interval: str,
        poll_interval: int = 60,
        kline_limit: int = 100,
        callback: Optional[Callable[[List[KlineData]], None]] = None,
    ):
        """
        Initialize kline poller.
        
        Args:
            client: MexcClient instance
            symbol: Trading pair symbol
            interval: Kline interval
            poll_interval: Polling interval in seconds
            kline_limit: Number of klines to fetch per poll
            callback: Callback function to invoke with new data
        """
        self.client = client
        self.symbol = symbol
        self.interval = interval
        self.poll_interval = poll_interval
        self.kline_limit = kline_limit
        self.callback = callback
        self.logger = get_logger(__name__)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_close_time: Optional[int] = None
    
    def set_callback(self, callback: Callable[[List[KlineData]], None]):
        """
        Set the callback function for new data.
        
        Args:
            callback: Callback function that receives list of KlineData
        """
        self.callback = callback
    
    async def start(self):
        """Start the polling loop."""
        if self._running:
            self.logger.warning("Poller is already running")
            return
        
        self._running = True
        self.logger.info(
            f"Starting kline poller for {self.symbol} "
            f"(interval={self.interval}, poll_interval={self.poll_interval}s)"
        )
        
        self._task = asyncio.create_task(self._poll_loop())
    
    async def stop(self):
        """Stop the polling loop."""
        if not self._running:
            return
        
        self.logger.info("Stopping kline poller...")
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        
        self.logger.info("Kline poller stopped")
    
    async def _poll_loop(self):
        """Main polling loop."""
        while self._running:
            try:
                klines = await self.client.get_klines(
                    symbol=self.symbol,
                    interval=self.interval,
                    limit=self.kline_limit,
                )
                
                if klines:
                    latest_close_time = klines[-1].close_time
                    
                    if self._last_close_time is None or latest_close_time > self._last_close_time:
                        self.logger.debug(
                            f"New kline data: close_time={klines[-1].close_time_dt}, "
                            f"close={klines[-1].close}"
                        )
                        self._last_close_time = latest_close_time
                        
                        if self.callback:
                            try:
                                if asyncio.iscoroutinefunction(self.callback):
                                    await self.callback(klines)
                                else:
                                    self.callback(klines)
                            except Exception as e:
                                self.logger.error(
                                    f"Error in callback function: {e}",
                                    exc_info=True
                                )
                    else:
                        self.logger.debug("No new kline data available")
                
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(
                    f"Error in polling loop: {e}",
                    exc_info=True
                )
                await asyncio.sleep(self.poll_interval)
        
        self.logger.info("Polling loop ended")
