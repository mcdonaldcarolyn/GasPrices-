import logging 
from datetime import date, timedelta
import httpx
import pandas as pd
from sqlalchemy.orm import Session
from app.config import settings
from app.models.db import RetailGasPrice

logger = logging.getLogger(__name__)

EIA_BASE = "https://api.eia.gov/v2/petroleum/pri/gnd/data"

print("eia.py loaded")

#I added all region labels, we can revisit to see of we need all of them
REGION_LABELS = {
    "regular_us":      "US",
    "midgrade_us":     "US",
    "premium_us":      "US",
    "diesel_us":       "US",
    "regular_east":    "East",
    "regular_midwest": "Midwest",
    "regular_gulf":    "Gulf",
    "regular_rocky":   "Rocky",
    "regular_west":    "West",
}

async def fetch_eia_series(
    series_id: str, 

    start: date | None= None, 
    end: date | None = None, 
) -> pd.DataFrame:

    if not settings.eia_api_key:
        raise ValueError("EIA_API_KEY not set in .env")

    params = {
        "api_key": settings.eia_api_key,
        "facets[series][]": series_id,
        "data[]": "value",
        "frequency": "weekly", 
        "sort[0][column]" : "period", 
        "sort[0][direction]": "asc", 
        "length": 5000,
    }
    if start:
        params["start"] = start.strftime("%Y-%m-%d")
    if end:
        params["end"] = end.strftime("%Y-%m-%d")


    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(EIA_BASE, params=params)
        resp.raise_for_status()

    data = resp.json()
    rows = data.get("response", {}).get("data", [])

    if not rows:
        logger.warning("EIA returned no data for series %s", series_id)
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df["period"] = pd.to_datetime(df["period"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df[["period", "value"]].dropna()

def transform_eia_df(df:pd.DataFrame, series_name: str, series_id: str) -> list[dict]:
    df = df.copy()
    df = df.rename(columns={"period": "price_date", "value": "price_usd"})
    df["price_date"] = df["price_date"].dt.date
    df["series_id"] = series_id
    df["region"] = REGION_LABELS.get(series_name, "Unknown")
    df["id"]= df.apply(lambda r: f"{series_id}_{r['price_date']}", axis=1)
    return df[["id", "series_id", "price_date", "price_usd", "region"]].to_dict(orient="records")


async def fetch_all_series(
    start: date | None = None,
    end: date | None = None,
) -> list[dict]:
    all_rows = []
    for series_name, series_id in settings.eia_series.items():
        df = await fetch_eia_series(series_id, start=start, end=end)
        if df.empty: 
            logger.warning("skipping %s - empty response", series_name)
            continue
        rows = transform_eia_df(df, series_name, series_id)
        logger.info("Fetched %d rows for %s", len(rows), series_name)
        all_rows.extend(rows)
    return all_rows

if __name__ == "__main__":
    import asyncio

    async def main():
          rows = await fetch_all_series()
          for row in rows[:5]:
              print(row)

asyncio.run(main())