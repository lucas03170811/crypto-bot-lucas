import aiohttp
import pandas as pd
import asyncio
from binance import AsyncClient

class BinanceClient:
    def __init__(self):
        self.client = asyncio.get_event_loop().run_until_complete(
            AsyncClient.create()
        )

    async def get_klines(self, symbol, interval="15m", limit=100):
        klines = await self.client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(klines, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["close"] = pd.to_numeric(df["close"])
        df["high"] = pd.to_numeric(df["high"])
        df["low"] = pd.to_numeric(df["low"])
        return df