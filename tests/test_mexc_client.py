"""Unit tests for MEXC client."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.mexc_client import (
    MexcClient,
    KlineData,
    KlinePoller,
    MexcClientError,
    MexcAPIError,
    MexcRateLimitError,
)


class TestKlineData:
    """Tests for KlineData class."""
    
    def test_from_api_response(self):
        """Test creating KlineData from API response."""
        api_data = [
            1609459200000,  # open_time
            "29000.00",     # open
            "29500.00",     # high
            "28800.00",     # low
            "29200.00",     # close
            "150.5",        # volume
            1609462800000,  # close_time
            "4380000.00",   # quote_volume
            1250,           # trades
            "75.25",        # taker_buy_base_volume
            "2190000.00",   # taker_buy_quote_volume
            "0",            # ignore
        ]
        
        kline = KlineData.from_api_response(api_data)
        
        assert kline.open_time == 1609459200000
        assert kline.open == 29000.00
        assert kline.high == 29500.00
        assert kline.low == 28800.00
        assert kline.close == 29200.00
        assert kline.volume == 150.5
        assert kline.close_time == 1609462800000
        assert kline.quote_volume == 4380000.00
        assert kline.trades == 1250
        assert kline.taker_buy_base_volume == 75.25
        assert kline.taker_buy_quote_volume == 2190000.00
    
    def test_to_dict(self):
        """Test converting KlineData to dictionary."""
        kline = KlineData(
            open_time=1609459200000,
            open=29000.00,
            high=29500.00,
            low=28800.00,
            close=29200.00,
            volume=150.5,
            close_time=1609462800000,
            quote_volume=4380000.00,
            trades=1250,
            taker_buy_base_volume=75.25,
            taker_buy_quote_volume=2190000.00,
        )
        
        result = kline.to_dict()
        
        assert result["open_time"] == 1609459200000
        assert result["close"] == 29200.00
        assert result["volume"] == 150.5
    
    def test_datetime_properties(self):
        """Test datetime conversion properties."""
        kline = KlineData(
            open_time=1609459200000,
            open=29000.00,
            high=29500.00,
            low=28800.00,
            close=29200.00,
            volume=150.5,
            close_time=1609462800000,
            quote_volume=4380000.00,
            trades=1250,
            taker_buy_base_volume=75.25,
            taker_buy_quote_volume=2190000.00,
        )
        
        assert isinstance(kline.open_time_dt, datetime)
        assert isinstance(kline.close_time_dt, datetime)


class TestMexcClient:
    """Tests for MexcClient class."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = MexcClient(
            base_url="https://api.mexc.com",
            max_retries=3,
            retry_delay=5,
            request_timeout=30,
        )
        
        assert client.base_url == "https://api.mexc.com"
        assert client.max_retries == 3
        assert client.retry_delay == 5
        assert client.request_timeout == 30
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with MexcClient() as client:
            assert client._client is not None
        
        assert client._client is None
    
    @pytest.mark.asyncio
    async def test_get_klines_success(self):
        """Test successful kline fetch."""
        mock_response_data = [
            [
                1609459200000, "29000.00", "29500.00", "28800.00", "29200.00",
                "150.5", 1609462800000, "4380000.00", 1250, "75.25", "2190000.00", "0"
            ],
            [
                1609462800000, "29200.00", "29600.00", "29100.00", "29400.00",
                "200.0", 1609466400000, "5880000.00", 1500, "100.0", "2940000.00", "0"
            ],
        ]
        
        async with MexcClient() as client:
            with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response_data
                
                klines = await client.get_klines("BTCUSDT", "1h", limit=2)
                
                assert len(klines) == 2
                assert klines[0].close == 29200.00
                assert klines[1].close == 29400.00
                
                mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_klines_with_time_range(self):
        """Test fetching klines with time range."""
        async with MexcClient() as client:
            with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = []
                
                await client.get_klines(
                    "BTCUSDT",
                    "1h",
                    limit=10,
                    start_time=1609459200000,
                    end_time=1609462800000,
                )
                
                call_args = mock_request.call_args
                params = call_args[0][2]
                
                assert params["startTime"] == 1609459200000
                assert params["endTime"] == 1609462800000
    
    @pytest.mark.asyncio
    async def test_get_latest_price(self):
        """Test getting latest price."""
        mock_response_data = [
            [
                1609459200000, "29000.00", "29500.00", "28800.00", "29200.00",
                "150.5", 1609462800000, "4380000.00", 1250, "75.25", "2190000.00", "0"
            ],
        ]
        
        async with MexcClient() as client:
            with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response_data
                
                price = await client.get_latest_price("BTCUSDT", "1h")
                
                assert price == 29200.00
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling."""
        async with MexcClient() as client:
            with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.side_effect = MexcAPIError(400, "Invalid symbol")
                
                with pytest.raises(MexcAPIError) as exc_info:
                    await client.get_klines("INVALID", "1h")
                
                assert exc_info.value.code == 400
                assert "Invalid symbol" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_rate_limit_handling(self):
        """Test rate limit error handling."""
        async with MexcClient(max_retries=1) as client:
            with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.side_effect = MexcRateLimitError("Rate limit exceeded")
                
                with pytest.raises(MexcRateLimitError):
                    await client.get_klines("BTCUSDT", "1h")


class TestKlinePoller:
    """Tests for KlinePoller class."""
    
    @pytest.mark.asyncio
    async def test_poller_initialization(self):
        """Test poller initialization."""
        client = MexcClient()
        
        poller = KlinePoller(
            client=client,
            symbol="BTCUSDT",
            interval="1h",
            poll_interval=60,
            kline_limit=100,
        )
        
        assert poller.symbol == "BTCUSDT"
        assert poller.interval == "1h"
        assert poller.poll_interval == 60
        assert poller.kline_limit == 100
        assert not poller._running
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_set_callback(self):
        """Test setting callback function."""
        client = MexcClient()
        poller = KlinePoller(client, "BTCUSDT", "1h")
        
        def callback(klines):
            pass
        
        poller.set_callback(callback)
        assert poller.callback == callback
        
        await client.close()
    
    @pytest.mark.asyncio
    async def test_poller_start_stop(self):
        """Test starting and stopping poller."""
        mock_klines = [
            KlineData(
                open_time=1609459200000,
                open=29000.00,
                high=29500.00,
                low=28800.00,
                close=29200.00,
                volume=150.5,
                close_time=1609462800000,
                quote_volume=4380000.00,
                trades=1250,
                taker_buy_base_volume=75.25,
                taker_buy_quote_volume=2190000.00,
            )
        ]
        
        async with MexcClient() as client:
            with patch.object(client, 'get_klines', new_callable=AsyncMock) as mock_get_klines:
                mock_get_klines.return_value = mock_klines
                
                callback_called = []
                
                def callback(klines):
                    callback_called.append(True)
                
                poller = KlinePoller(
                    client,
                    "BTCUSDT",
                    "1h",
                    poll_interval=1,
                    callback=callback,
                )
                
                await poller.start()
                assert poller._running
                
                await asyncio.sleep(2)
                
                await poller.stop()
                assert not poller._running
                
                assert len(callback_called) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
