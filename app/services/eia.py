import logging 
from datetime import date, timedelta
import httpx
import pandas as pd
from sqlalchemy.orm import Session
from app.config import settings
from app.models.db import RetailGasPrice

logger = logging.getLogger(__name__)

EIA_BASE = "https://api.eia.gov/v2/petroleum/pri/gnd/data"

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
