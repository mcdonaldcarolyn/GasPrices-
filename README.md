# GasPrices-

This project tracks retail gas prices, crude oil, and macroeconomic signals.

## Database utility helpers

The repository includes a helper module for loading and saving pandas DataFrames from/to the database:

- `app/models/utils.py`
- exported from `app/models/__init__.py`

### Example usage

```python
import pandas as pd
from app.models import read_table, write_dataframe

# Load a full table into a DataFrame
pricing_df = read_table("retail_gas_prices")

# Run a query into a DataFrame
query = "SELECT * FROM retail_gas_prices WHERE price_date >= '2020-01-01'"
recent_df = read_query(query)

# Write transformed results back to the database
write_dataframe(recent_df, "recent_pricing", if_exists="append")
```

### Bulk insert with ORM models

If you want to insert DataFrame rows using a SQLAlchemy model, use:

```python
from app.models import bulk_insert_from_dataframe
from app.models.db import Session, EnergyForecast

with Session() as session:
    bulk_insert_from_dataframe(session, EnergyForecast, df)
```

## Requirements

Install dependencies before running the helper:

```bash
pip install -r requirements.txt
```
