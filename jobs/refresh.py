from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import text
from db.session import engine
from data.twelve import get_prices
from data.ust import get_treasury_yields
from db.io import write_prices, write_yields

sched = BlockingScheduler()

@sched.scheduled_job("interval", minutes=60)
def refresh_data():
    """Function to run in the background to call the APIs every hour, clean the data, and refresh the database"""
    
    tickers = ["SPY", "NDAQ", "TLT", "GLD"]
    print("Fetching data...")
    prices = get_prices(tickers)
    write_prices(prices, schema="bronze", table="twelve_price")
    
    # Treasury data
    ust = get_treasury_yields()
    write_yields(ust, schema="bronze", table="ts_yield")

    # Clean step: insert filtered data into clean schema
    clean_prices_sql = text("""
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
                SELECT 1
                FROM clean.twelve_price AS c
                WHERE c.ts = r.ts
                    AND c.ticker = r.ticker
        );
    """) #Validation checks when importing the data for stock data
    
    # Clean step: insert filtered data into clean schema
    clean_yields_sql = text("""
        INSERT INTO clean.ts_yield (
            record_date, 
            avg_interest_rate_amt
            )
        SELECT record_date, avg_interest_rate_amt
        FROM bronze.ts_yield r
        WHERE avg_interest_rate_amt > 0
        AND record_date IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM clean.ts_yield AS c
            WHERE c.record_date = r.record_date
  );
    """) #Validation checks when importing the data for yields data

    with engine.begin() as conn:
        conn.execute(clean_prices_sql)
        conn.execute(clean_yields_sql)



    print("Data refreshed and cleaned")

if __name__ == "__main__":
    print("Initial load...")
    refresh_data()
    print("Starting hourly updates...")
    sched.start() #python3 -m jobs.refresh #to run