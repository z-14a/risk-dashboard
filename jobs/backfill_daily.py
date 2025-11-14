"""
Backfill 2 years of daily OHLC data into bronze schema.
Run once before starting hourly refresh job.
"""

from data.twelve import get_prices
from db.io import write_prices
from sqlalchemy import text
from db.session import engine


def backfill_daily():
    tickers = ["SPY", "NDAQ", "TLT", "GLD"]

    print("Fetching 2-year daily data...")
    prices = get_prices(
        tickers,
        interval="1day",
        outputsize= 600  # Twelve Data parameter to fetch max history
    )

    print("Writing to bronze schema...")
    write_prices(prices, schema="bronze", table="twelve_price")

    print("Running cleaning pipeline...")

    clean_sql = text("""
        INSERT INTO clean.twelve_price (
            ts, 
            ticker, 
            open_price, 
            high_price, 
            low_price, 
            close_price, 
            volume
        )
        SELECT 
            r.ts, r.ticker, r.open_price, r.high_price, r.low_price, r.close_price, r.volume
        FROM bronze.twelve_price r
        WHERE r.close_price > 0
            AND r.volume >= 0
            AND r.high_price >= GREATEST(r.open_price, r.close_price)
            AND r.low_price <= LEAST(r.open_price, r.close_price)
            AND r.ts IS NOT NULL
            AND r.ticker IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM clean.twelve_price c
                WHERE c.ts = r.ts
                  AND c.ticker = r.ticker
            );
    """)

    with engine.begin() as conn:
        conn.execute(clean_sql)

    print("Daily backfill completed.")


if __name__ == "__main__":
    backfill_daily()