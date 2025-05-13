import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_data(symbol: str, period: str="7d", interval: str="15m") -> pd.DataFrame:
    """
    Fetch historical price data for a given stock symbol.

    :param symbol: Ticker symbol (e.g., "APPL")
    :param period: Lookback window (e.g., "1d", "5d", "7d", "1mo")
    :param interval: Granularity (e.g., "1m", "5m", "15m", "1d")
    :return: DataFrame with price data
    """
    try: 
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            raise ValueError("No data returned by yfinance.")
        
        df.reset_index(inplace=True)
        df.rename(columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        df['symbol'] = symbol
        return df
    
    except Exception as e:
        print(f"[collector] Error fetching data for {symbol}: {e}")
        return pd.DataFrame()