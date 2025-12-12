# MEXC Client Implementation

## Overview

This document describes the implementation of the MEXC client module for the MEXC EMA Bot project.

## What Was Implemented

### 1. MEXC Client Module (`src/bot/mexc_client.py`)

A comprehensive client for interacting with the MEXC REST API with the following features:

#### Core Components

##### `MexcClient`
- **Purpose**: Async HTTP client for MEXC REST API interactions
- **Key Features**:
  - Fetches kline/candlestick data from `/api/v3/klines` endpoint
  - Automatic retry with exponential backoff
  - Rate limit detection and handling
  - Network error recovery with configurable retries
  - Context manager support for proper resource cleanup
  - Structured logging of all operations

- **Main Methods**:
  - `get_klines(symbol, interval, limit, start_time, end_time)` - Fetch historical candlestick data
  - `get_latest_price(symbol, interval)` - Get the latest close price

- **Configuration Parameters**:
  - `base_url` - MEXC API base URL (default: https://api.mexc.com)
  - `max_retries` - Maximum retry attempts (default: 3)
  - `retry_delay` - Initial retry delay in seconds (default: 5)
  - `request_timeout` - Request timeout in seconds (default: 30)

##### `KlinePoller`
- **Purpose**: Continuous polling loop for real-time market data
- **Key Features**:
  - Polls for new kline data at configurable intervals
  - Invokes callback functions with new data
  - Supports both sync and async callbacks
  - Tracks last close_time to avoid duplicate processing
  - Graceful start/stop with proper cleanup

- **Usage**:
  ```python
  poller = KlinePoller(
      client=client,
      symbol="BTCUSDT",
      interval="60m",
      poll_interval=60,
      kline_limit=100,
      callback=on_new_data
  )
  await poller.start()
  # ... bot logic ...
  await poller.stop()
  ```

##### `KlineData`
- **Purpose**: Dataclass representing a single candlestick
- **Fields**:
  - `open_time` - Opening time in milliseconds
  - `open` - Opening price
  - `high` - Highest price
  - `low` - Lowest price
  - `close` - Closing price
  - `volume` - Trading volume
  - `close_time` - Closing time in milliseconds
  - `quote_volume` - Quote asset volume
  - `trades` - Number of trades
  - `taker_buy_base_volume` - Taker buy base volume
  - `taker_buy_quote_volume` - Taker buy quote volume

- **Methods**:
  - `from_api_response(data)` - Create from MEXC API response array
  - `to_dict()` - Convert to dictionary
  - `open_time_dt` - Property for datetime conversion
  - `close_time_dt` - Property for datetime conversion

##### `KlineInterval` Enum
- Defines valid interval values: 1m, 5m, 15m, 30m, 60m, 4h, 1d, 1w, 1M

##### Exception Classes
- `MexcClientError` - Base exception
- `MexcAPIError` - API errors with code and message
- `MexcRateLimitError` - Rate limit exceeded

### 2. Configuration Updates (`src/bot/config.py`)

Added new configuration parameters:
- `MEXC_BASE_URL` - API base URL (default: https://api.mexc.com)
- `KLINE_LIMIT` - Number of klines per request (default: 100, max: 1000)
- `POLL_INTERVAL` - Polling interval in seconds (default: 60)
- `MAX_RETRIES` - Maximum retry attempts (default: 3)
- `RETRY_DELAY` - Initial retry delay in seconds (default: 5)
- `REQUEST_TIMEOUT` - Request timeout in seconds (default: 30)

Added helper method:
- `_get_env_as_float()` - Get environment variable as float

### 3. Unit Tests (`tests/test_mexc_client.py`)

Comprehensive test suite with 13 tests covering:
- `KlineData` creation and serialization
- `MexcClient` initialization and lifecycle
- Kline fetching with various parameters
- Error handling (API errors, rate limits)
- `KlinePoller` initialization and operation

All tests use mocking to avoid actual API calls during testing.

### 4. Example Scripts (`examples/test_mexc_client.py`)

Demonstration script showing:
- Simple kline data fetching
- Continuous polling with callbacks
- Proper error handling
- Configuration integration

### 5. Documentation Updates

- Updated `README.md` with:
  - MEXC Client architecture section
  - Usage examples
  - Configuration options
  - Testing instructions
  
- Updated `.env.example` with new configuration parameters

## Technical Details

### API Integration

The client uses the MEXC REST API v3:
- **Endpoint**: `GET /api/v3/klines`
- **Parameters**:
  - `symbol` - Trading pair (e.g., BTCUSDT)
  - `interval` - Kline interval (1m, 5m, 15m, 30m, 60m, 4h, 1d, 1w, 1M)
  - `limit` - Number of klines (max 1000)
  - `startTime` - Optional start time in milliseconds
  - `endTime` - Optional end time in milliseconds

- **Response**: Array of arrays, each containing 8 fields:
  ```json
  [
    [
      1609459200000,  // open_time
      "29000.00",     // open
      "29500.00",     // high
      "28800.00",     // low
      "29200.00",     // close
      "150.5",        // volume
      1609462800000,  // close_time
      "4380000.00"    // quote_volume
    ]
  ]
  ```

### Error Handling Strategy

1. **Network Errors**: Retry with exponential backoff
2. **Rate Limits**: Wait and retry (respects X-MBX-USED-WEIGHT-1M header)
3. **API Errors**: Retry only for retryable codes (500, 502, 503, 504, -1001, -1021)
4. **Timeout**: Configurable request timeout with retry logic

### Rate Limiting

The client tracks rate limit usage via response headers:
- Monitors `x-mbx-used-weight-1m` header
- Calculates remaining capacity (1200 - used_weight)
- Automatically delays requests when approaching limits

### Async Implementation

- Built on `httpx` for high-performance async HTTP
- Uses `asyncio` for polling loop and async operations
- Context manager support for proper resource cleanup
- Compatible with async/await patterns throughout the bot

## Testing

### Unit Tests
```bash
pytest tests/test_mexc_client.py -v
```

### Integration Test (requires .env configuration)
```bash
python examples/test_mexc_client.py
```

## Dependencies

Added to `requirements.txt`:
- `httpx==0.26.0` - Async HTTP client (already present)
- All other dependencies were already in place

## Future Enhancements

Potential improvements for future iterations:
1. WebSocket support for real-time streaming
2. Additional endpoints (ticker, orderbook, trades)
3. Connection pooling and request batching
4. Circuit breaker pattern for fault tolerance
5. Metrics and monitoring integration
6. Request caching for frequently accessed data

## Notes

- The MEXC API does not require authentication for public endpoints (like klines)
- API credentials in config are for future private endpoint support
- Interval format uses MEXC's standard: 1m, 5m, 15m, 30m, 60m, 4h, 1d, 1w, 1M
- The client is production-ready with robust error handling and logging
