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
        
)