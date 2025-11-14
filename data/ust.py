import requests
import pandas as pd

UST_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"

def get_treasury_yields(limit=30):
    params = {
        "page[number]": 1,
        "page[size]": limit,
        "sort": "-record_date"
    }
    r = requests.get(UST_URL, params=params, timeout=10)
    r.raise_for_status()
    js = r.json()

    data = js.get("data", [])
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["record_date"] = pd.to_datetime(df["record_date"])
    return df[["record_date", "avg_interest_rate_amt"]]