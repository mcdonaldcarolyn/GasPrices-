import pandas as pd


def get_df() -> pd.DataFrame:
    """Takes a DB session and returns prepared DataFrame"""
    df = pd.DataFrame({})
    return df


def predict_price_rise(df: pd.DataFrame) -> float:
    """Logistic Regression Pipeline that returns a probability"""
    return 1.0


def predict_gas_prices(df: pd.DataFrame):
    """RandomForest Pipeline that returns gas price predictions"""
    pass
