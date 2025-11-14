import pandas as pd
from sqlalchemy import text
from .session import engine

def write_prices(df: pd.DataFrame, schema: str, table:str) -> None:
    """Stages data to be sent from the API call to the database"""
    df.to_sql(table, engine, schema= schema, if_exists="append", index=False)

def write_yields(df: pd.DataFrame, schema: str, table:str) -> None:
    """Stages data to be sent from the API call to the database"""
    df.to_sql(table, engine, schema = schema, if_exists="append", index=False)
       



def read_prices(limit=None) -> pd.DataFrame:
    """Retrieves stock data from cleaned database"""
    
    base_query = "SELECT * FROM clean.twelve_price ORDER BY ts ASC"
    params = {}
    if limit:
        base_query += " LIMIT :limit"
        params = {"limit": limit}

    with engine.connect() as conn:
        df = pd.read_sql(text(base_query), conn, params=params)
    #Data cleaning
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df["ticker"] = df["ticker"].astype("category")
    df = df.sort_values(["ticker", "ts"])
    df = df[df["close_price"] > 0]
    df = df[df["volume"] >= 0]
    
    df = df.rename(columns={
    "ts": "datetime",
    "close_price": "close",
    "open_price": "open",
    "high_price": "high",
    "low_price": "low",
    })
    df["return"] = df.groupby("ticker")["close"].pct_change()

    assert df["close"].notna().all()
    return df
    
def read_yields(limit=None) -> pd.DataFrame:
    """Retrieves treasury yield data from cleaned database"""
    
    query = "SELECT * FROM clean.treasury_yields ORDER BY record_date ASC"
    params = {}
    if limit:
        query += " LIMIT :limit"
        params = {"limit": limit}
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params, parse_dates=["record_date"])
    return df   
    
    
    
    
    
#One of the main issues, was that I wanted historical data for at least 2 years.
#I wanted to have hourly data for the dashboard, but for historical data, I had to use daily data due to limits on the API Call
#This was really confusing for me to solve, so I had to use AI to build a function to separate the pricing data
def separate_hourly_daily(df: pd.DataFrame) -> list[pd.DataFrame, pd.DataFrame]: 
    """
    Separates hourly and daily price data based on bar frequency per day.
    
    Logic (corrected for DST issues):
    - Daily data: minute == 0 (00 at timestamp), possibly at hours 0, 23, or 8 (DST shift)
    - Hourly data: minute == 30 (always for intraday OHLC)
    
    Args:
        df: DataFrame with columns [datetime, ticker, open, high, low, close, volume]
        
    Returns:
        list: [daily_df, hourly_df] - two separated DataFrames
    """
    
    df = df.copy()

    # Ensure datetime is timezone-aware UTC
    if df["datetime"].dt.tz is None:
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    
    # Extract useful components
    df["date"] = df["datetime"].dt.date
    df["hour"] = df["datetime"].dt.hour
    df["minute"] = df["datetime"].dt.minute
    
    # Count bars per day per ticker
    df["bars_per_day"] = df.groupby(["ticker", "date"])["datetime"].transform("count")

    # === Corrected classification ===
    # Daily data always has minute == 0
    is_daily = df["minute"] == 0

    # Hourly data always has minute == 30
    is_hourly = df["minute"] == 30

    # Split
    daily_df = df[is_daily].copy()
    hourly_df = df[is_hourly].copy()

    # -------------------------
    # POST-PROCESS DAILY DATA
    # -------------------------
    if len(daily_df) > 0:

        # Fix daily bars at 23:00 → shift to next day 00:00
        mask_23h = (daily_df["hour"] == 23) & (daily_df["minute"] == 0)
        daily_df.loc[mask_23h, "datetime"] = (
            daily_df.loc[mask_23h, "datetime"] + pd.Timedelta(hours=1)
        )

        # Fix daily bars at 08:00 or 08:30 (DST fallback)
        mask_dst = (daily_df["hour"] == 8)
        daily_df.loc[mask_dst, "datetime"] = (
            daily_df.loc[mask_dst, "datetime"] + pd.Timedelta(hours=1)
        )

        # Normalise to midnight
        daily_df["datetime"] = daily_df["datetime"].dt.normalize()

        # Remove duplicates (same day & ticker)
        daily_df = daily_df.sort_values(["ticker", "datetime"])
        daily_df = daily_df.drop_duplicates(subset=["ticker", "datetime"], keep="first")

    # -------------------------
    # POST-PROCESS HOURLY DATA
    # -------------------------
    if len(hourly_df) > 0:
        # Validate hours (expected trading window)
        in_trading_hours = (
            ((hourly_df["hour"] == 9) & (hourly_df["minute"] == 30)) |
            ((hourly_df["hour"] >= 10) & (hourly_df["hour"] <= 14)) |
            ((hourly_df["hour"] == 15) & (hourly_df["minute"] == 30))
        )

        outside_hours = hourly_df[~in_trading_hours]
        if len(outside_hours) > 0:
            print(f"⚠️  Warning: {len(outside_hours)} hourly bars outside expected trading hours")
            print(f"   Hours: {sorted(outside_hours['hour'].unique())}")
            print(f"   Minutes: {sorted(outside_hours['minute'].unique())}")

        # Remove duplicates
        hourly_df = hourly_df.drop_duplicates(subset=["ticker", "datetime"], keep="first")

    # Cleanup
    cols_to_drop = ["date", "hour", "minute", "bars_per_day"]
    daily_df = daily_df.drop(columns=cols_to_drop, errors="ignore").reset_index(drop=True)
    hourly_df = hourly_df.drop(columns=cols_to_drop, errors="ignore").reset_index(drop=True)

    return daily_df, hourly_df