import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models.db import create_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    logger.info("Database tables ready.")
    yield


app = FastAPI(
    title="Gas Price API",
    description="Track retail gas prices, crude oil, and macro signals.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["health"])
def root():
    return {"status": "ok", "message": "Gas Price API running. Visit /docs for the full API."}
