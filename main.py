import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.models.db import create_tables, engine
from app.routers import prices, ingest, stats
from app.services.eia import ingest_gas_prices
from app.services.fred import ingest_crude_prices, ingest_macro_signals

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def _scheduled_ingest():
    """Runs automatically on a schedule to pull fresh data."""
    logger.info("Scheduled ingest starting...")
    with Session(engine) as db:
        await ingest_gas_prices(db)
        await ingest_crude_prices(db)
        await ingest_macro_signals(db)
    logger.info("Scheduled ingest complete.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- everything before yield runs on startup ---
    create_tables()
    logger.info("Database tables ready.")

    scheduler.add_job(
        _scheduled_ingest,
        CronTrigger(day_of_week="mon", hour=22, minute=0),
        id="weekly_ingest",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started.")

    yield  # app is running here, handling requests

    # --- everything after yield runs on shutdown ---
    scheduler.shutdown()
    logger.info("Scheduler stopped.")

app = FastAPI(
    title="Gas Price API",
    description="Track retail gas prices, crude oil, and macro signals.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(prices.router)
app.include_router(ingest.router)
app.include_router(stats.router)

@app.get("/", tags=["health"])
def root():
    return {
        "status": "ok",
        "message": "Gas Price API running. Visit /docs for the full API.",
        "quick_start": [
            "POST /ingest/all?days_back=365",
            "GET  /prices/latest",
            "GET  /stats/regression",
            "GET  /stats/probability",
        ],
    }