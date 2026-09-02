import logging
from datetime import date
import httpx
import pandas as pd
from app.config import settings

logger = logging.getLogger(__name__)

FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

SERIES_LABELS = {
      "brent_crude": "Brent Crude",
      "wti_crude":   "WTI Crude",
      "gas_weekly":  "US Regular Gas",
  }

async def fetch_fred_series(
        series_id: str, 
        start: date | None = None, 
        end: date | None = None,
) -> pd.DataFrame:
    if not settings.fred_api_key: 
        raise ValueError("FRED_API_Key not set in .env")
    params = {
        "series_id": series_id, 
        "api_key": settings.fred_api_key,
        "file_type": "json", 
        "sort_order": "asc",
    }
    if start:
        params["observation_start"] = start.strftime("%Y-%m-%d")
    if end: 
        params["observation_end"] = end.strftime("%Y-%m-%d")

    async with httpx.AsyncClient(timeout=30) as client: 
        resp = await client.get(FRED_BASE, params=params)
        resp.raise_for_status()

    rows = resp.json().get("observations", [])

    if not rows:
        logger.warning("Fred returned no data fro series %s", series_id)
        return pd.DataFrame()
    
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df[["date", "value"]].dropna()

def transform_fred_df(df: pd.DataFrame, series_name: str, series_id: str) -> list[dict]:
    df = df.copy()
    df = df.rename(columns={"date": "price_date", "value": "price_usd"})
    df["price_date"] = df["price_date"].dt.date
    df["series_id"] = series_name
    df["series_name"] = SERIES_LABELS.get(series_name, "Unknown")
    df["id"] = df.apply(lambda r: f"{series_name}_{r['price_date']}", axis=1)
    return df[["id", "series_id", "series_name", "price_date", "price_usd"]].to_dict(orient="records")

async def fetch_all_fred_series(
    start: date | None = None, 
    end: date | None = None,
) -> list[dict]:
    all_rows = []
    for series_name, series_id in settings.fred_series.items():
        df = await fetch_fred_series(series_id, start=start, end=end)
        if df.empty:
            logger.warning("Skipping %s - empty response", series_name)
            continue
        rows = transform_fred_df(df, series_name, series_id)
        logger.info("fetched %d rows for %s", len(rows), series_name)
        all_rows.extend(rows)
    return all_rows

if __name__ == "__main__":
    import asyncio

    async def main():
        print("starting FRED fetch..")
        rows = await fetch_all_fred_series(end=date.today())
        print(f"total rows return: {len(rows)}")
        for row in rows[-5:]:
            print(row)
    asyncio.run(main())