import ccxt
import pandas as pd
import ta
import time
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT']
timeframe = '5m'
limit = 100
trade_amounts = {
    'BTC/USDT': 0.001,
    'ETH/USDT': 0.01,
    'SOL/USDT': 0.5,
    'XRP/USDT': 10
}

def fetch_data(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def add_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    return df

def signal(df):
    if df['rsi'].iloc[-1] < 30 and df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
        return 'buy'
    elif df['rsi'].iloc[-1] > 70 and df['macd'].iloc[-1] < df['macd_signal'].iloc[-1]:
        return 'sell'
    return 'hold'

def place_order(symbol, order_type):
    amount = trade_amounts.get(symbol, 0)
    if amount == 0:
        return
    if order_type == 'buy':
        exchange.create_market_buy_order(symbol, amount)
        print(f"✅ 買入 {symbol}")
    elif order_type == 'sell':
        exchange.create_market_sell_order(symbol, amount)
        print(f"✅ 賣出 {symbol}")

while True:
    try:
        for symbol in symbols:
            df = fetch_data(symbol)
            df = add_indicators(df)
            action = signal(df)
            print(f"[{symbol}] 判斷結果：{action}")
            if action != 'hold':
                place_order(symbol, action)
        time.sleep(300)
    except Exception as e:
        print(f"⚠️ 錯誤：{e}")
        time.sleep(60)