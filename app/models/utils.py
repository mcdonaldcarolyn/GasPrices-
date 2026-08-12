from __future__ import annotations

from typing import Any

import pandas as pd
from pandas import DataFrame
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def _default_engine() -> Engine:
    from app.models.db import engine

    return engine


def read_table(table_name: str, con: Engine | None = None, **kwargs: Any) -> DataFrame:
    """Load a full database table into a pandas DataFrame."""
    connection = con if con is not None else _default_engine()
    return pd.read_sql_table(table_name, con=connection, **kwargs)


def read_query(sql: str, con: Engine | None = None, params: dict[str, Any] | None = None, **kwargs: Any) -> DataFrame:
    """Run a SQL query and return the results as a pandas DataFrame."""
    connection = con if con is not None else _default_engine()
    if params is not None:
        sql = text(sql)
    return pd.read_sql_query(sql, con=connection, params=params, **kwargs)


def write_dataframe(df: DataFrame, table_name: str, con: Engine | None = None, *, if_exists: str = "append", index: bool = False, method: str | None = "multi", **kwargs: Any) -> None:
    """Write a pandas DataFrame into a database table."""
    connection = con if con is not None else _default_engine()
    df.to_sql(table_name, con=connection, if_exists=if_exists, index=index, method=method, **kwargs)


def bulk_insert_from_dataframe(session: Session, model: type[Any], df: DataFrame) -> None:
    """Bulk insert DataFrame rows into a SQLAlchemy ORM model table."""
    records = df.to_dict(orient="records")
    session.bulk_insert_mappings(model, records)
    session.commit()
