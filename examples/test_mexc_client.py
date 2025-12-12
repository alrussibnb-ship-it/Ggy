"""Example script to test MEXC client functionality."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from bot.config import BotConfig
from bot.logger import setup_logger
from bot.mexc_client import MexcClient, KlinePoller, KlineData
from typing import List


async def simple_fetch_example():
    """Simple example of fetching kline data."""
    print("\n=== Simple Fetch Example ===\n")
    
    config = BotConfig()
    setup_logger("bot", level=config.log_level)
    
    async with MexcClient(
        base_url=config.mexc_base_url,
        max_retries=config.max_retries,
        retry_delay=config.retry_delay,
        request_timeout=config.request_timeout,
    ) as client:
        interval = config.interval if config.interval else "60m"
        
        klines = await client.get_klines(
            symbol=config.default_symbol,
            interval=interval,
            limit=10,
        )
        
        print(f"\nFetched {len(klines)} klines for {config.default_symbol}:")
        print(f"{'Time':<20} {'Open':<12} {'High':<12} {'Low':<12} {'Close':<12} {'Volume':<15}")
        print("-" * 90)
        
        for kline in klines[-5:]:
            print(
                f"{kline.open_time_dt.strftime('%Y-%m-%d %H:%M'):<20} "
                f"{kline.open:<12.2f} "
                f"{kline.high:<12.2f} "
                f"{kline.low:<12.2f} "
                f"{kline.close:<12.2f} "
                f"{kline.volume:<15.4f}"
            )
        
        latest_price = await client.get_latest_price(
            config.default_symbol,
            interval
        )
        print(f"\nLatest close price: {latest_price:.2f}")


async def polling_example():
    """Example of using the kline poller."""
    print("\n=== Polling Example ===\n")
    print("Polling for new kline data (will run for 3 cycles)...\n")
    
    config = BotConfig()
    setup_logger("bot", level=config.log_level)
    
    call_count = [0]
    interval = config.interval if config.interval else "60m"
    
    def on_new_klines(klines: List[KlineData]):
        """Callback for new kline data."""
        call_count[0] += 1
        latest = klines[-1]
        print(f"\n[Callback #{call_count[0]}] New kline data received!")
        print(f"  Symbol: {config.default_symbol}")
        print(f"  Time: {latest.close_time_dt}")
        print(f"  Close: {latest.close:.2f}")
        print(f"  Volume: {latest.volume:.4f}")
        print(f"  Total klines: {len(klines)}")
    
    async with MexcClient(
        base_url=config.mexc_base_url,
        max_retries=config.max_retries,
        retry_delay=config.retry_delay,
        request_timeout=config.request_timeout,
    ) as client:
        poller = KlinePoller(
            client=client,
            symbol=config.default_symbol,
            interval=interval,
            poll_interval=10,
            kline_limit=config.kline_limit,
            callback=on_new_klines,
        )
        
        await poller.start()
        
        try:
            for i in range(3):
                print(f"\nWaiting for cycle {i+1}/3...")
                await asyncio.sleep(12)
        finally:
            await poller.stop()
    
    print("\n✓ Polling example completed")


async def main():
    """Run all examples."""
    try:
        await simple_fetch_example()
        await asyncio.sleep(2)
        await polling_example()
        
        print("\n✓ All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
