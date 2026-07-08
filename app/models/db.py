from datetime import date
from sqlalchemy import create_engine, Column, String, Float, Date, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Session
from app.config import settings


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)


class Base(DeclarativeBase):
    pass


class RetailGasPrice(Base):
    __tablename__ = "retail_gas_prices"

    id         = Column(String, primary_key=True)
    series_id  = Column(String, index=True)
    price_date = Column(Date, index=True)
    price_usd  = Column(Float)
    region     = Column(String, default="US")
    fetched_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<RetailGasPrice {self.series_id} {self.price_date} ${self.price_usd:.3f}/gal>"


class CrudeOilPrice(Base):
    __tablename__ = "crude_oil_prices"

    id         = Column(String, primary_key=True)
    series_id  = Column(String, index=True)
    price_date = Column(Date, index=True)
    price_usd  = Column(Float)
    fetched_at = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<CrudeOilPrice {self.series_id} {self.price_date} ${self.price_usd:.2f}/bbl>"


class MacroSignal(Base):
    __tablename__ = "macro_signals"

    id          = Column(String, primary_key=True)
    series_id   = Column(String, index=True)
    signal_date = Column(Date, index=True)
    value       = Column(Float)
    fetched_at  = Column(DateTime, server_default=func.now())

    def __repr__(self):
        return f"<MacroSignal {self.series_id} {self.signal_date} = {self.value}>"


def create_tables():
    if "sqlite" in settings.database_url:
        from pathlib import Path
        db_path = settings.database_url.replace("sqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency that yields a DB session."""
    with Session(engine) as session:
        yield session