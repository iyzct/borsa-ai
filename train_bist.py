import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import numpy as np

tickers = [
    "THYAO.IS",
    "ASELS.IS",
    "KCHOL.IS",
    "BIMAS.IS",
    "TUPRS.IS"
]

rows = []

for ticker in tickers:

    print("PROCESSING:", ticker)

    df = yf.download(ticker, period="5y")

    # MultiIndex cleanup
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty or len(df) < 200:
        continue

    # Features
    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()

    df["momentum"] = (
        df["Close"] / df["Close"].shift(20)
    ) - 1

    df["volume_change"] = (
        df["Volume"] / df["Volume"].shift(20)
    ) - 1

    df = df.dropna()

    # Sliding window
    for i in range(100, len(df) - 63):

        today = df.iloc[i]
        future = df.iloc[i + 63]

        price_change = (
            (future["Close"] - today["Close"])
            / today["Close"]
        )

        target = int(price_change > 0.07)

        rows.append({
            "ma20": float(today["ma20"]),
            "ma50": float(today["ma50"]),
            "momentum": float(today["momentum"]),
            "volume_change": float(today["volume_change"]),
            "target": target
        })

# Create dataframe
data = pd.DataFrame(rows)

# Remove NaN
data = data.dropna()

# Features / target
X = data.drop("target", axis=1)
y = data["target"]

# Convert all to float
X = X.astype(float)

# Remove inf values
X = X.replace(np.inf, np.nan)
X = X.replace(-np.inf, np.nan)

# Remove invalid rows
X = X.dropna()

# Align target indexes
y = y.loc[X.index]

print("TOTAL TRAINING ROWS:", len(X))

# Model
model = RandomForestClassifier(
    n_estimators=400,
    max_depth=8,
    random_state=42
)

# Train
model.fit(X, y)

# Save
joblib.dump(model, "model_bist.pkl")

print("BIST MODEL READY")