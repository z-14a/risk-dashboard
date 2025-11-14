import requests
import pandas as pd
from datetime import datetime
from config import TWELVE_API_KEY

BASE = "https://api.twelvedata.com/time_series"

def get_prices(tickers: list, interval="1h", outputsize = 200) -> list:
    """Calls API to retrieve hourly data from the twelve data API, and returns a list of dataframes"""
    
    frames = []

    for t in tickers:
        params = {
            "symbol": t,
            "interval": interval,
            "apikey": TWELVE_API_KEY,
            "outputsize": outputsize
        }
        r = requests.get(BASE, params=params, timeout=10)
        r.raise_for_status()
        js = r.json()

        if "values" not in js:
            raise ValueError(f"Bad API reply for {t}: {js}")

        df = pd.DataFrame(js["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df["ticker"] = t
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype(float)
        df.rename(columns={
        "datetime": "ts",
        "open": "open_price",
        "high": "high_price",
        "low": "low_price",
        "close": "close_price"
        }, inplace=True)
        
        frames.append(df[["ts", "ticker", "open_price", "high_price", "low_price", "close_price", "volume"]])
    
    return pd.concat(frames).sort_values("ts")

