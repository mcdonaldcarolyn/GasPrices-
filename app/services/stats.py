import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestRegressor
from sqlalchemy import Session


def get_df(session: Session) -> pd.DataFrame:
    """Takes a DB session and returns prepared DataFrame"""
    # TODO:
    df = pd.DataFrame({})
    return df


def get_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str] = None,
) -> ColumnTransformer:
    """Standardized preprocessor"""
    categorical_features = categorical_features or []

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    return ColumnTransformer(transformers=[
        ("num", numeric_transformer, numeric_features),
        ("cat", categorical_transformer, categorical_features)
    ])


def predict_price_rise(df: pd.DataFrame) -> float:
    """Logistic Regression Pipeline that returns a probability"""
    # TODO: decide features based on schema
    numeric_features = []
    categorical_features = []
    target = ""

    X = df[numeric_features + categorical_features]
    y = df[target]

    pipeline = Pipeline(steps=[
        ("preprocessor", get_preprocessor(numeric_features, categorical_features)),
        ("classifier", LogisticRegression(random_state=42))
    ])
    pipeline.fit(X, y)
    # Assumes last observation is most recent
    probability_rise = pipeline.predict_proba(X.iloc[[-1]])
    return float(probability_rise)


def predict_gas_prices(df: pd.DataFrame) -> float:
    """RandomForest Pipeline that returns gas price predictions"""
    numeric_features = []
    categorical_features = []
    target = ""

    X = df[numeric_features + categorical_features]
    y = df[target]

    pipeline = Pipeline(steps=[
        ("preprocessor", get_preprocessor(numeric_features, categorical_features)),
        ("regressor", RandomForestRegressor(random_state=42))
    ])
    pipeline.fit(X, y)
    # TODO: predicting latest observation as placeholder
    predicted_price = pipeline.predict(X.iloc[[-1]])[0]
    return round(float(predicted_price), 2)
