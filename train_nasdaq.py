import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "HL"]

rows = []

for ticker in tickers:
    print("İŞLENİYOR:", ticker)
    t = yf.Ticker(ticker)
    df = t.history(period="5y")

    if df.empty or len(df) < 200:
        continue

    # Teknik göstergeler
    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()

    # Bilanço (sabit, günlük değişmez)
    info = t.info
    profit_margin = info.get("profitMargins")
    debt_to_equity = info.get("debtToEquity")
    pe = info.get("trailingPE")
    revenue_growth = info.get("revenueGrowth")

    if None in (profit_margin, debt_to_equity, pe, revenue_growth):
        continue

    # KAYAN PENCERE: her gün bir örnek
    for i in range(100, len(df) - 126):
        today = df.iloc[i]
        future = df.iloc[i + 126]

        price_change = (future["Close"] - today["Close"]) / today["Close"]

        # %5 üzeri yükseliş = AL
        target = int(price_change > 0.05)

        rows.append({
            "ma20": today["ma20"],
            "ma50": today["ma50"],
            "profit_margin": profit_margin,
            "debt_to_equity": debt_to_equity,
            "pe": pe,
            "revenue_growth": revenue_growth,
            "target": target
        })

# DATAFRAME
data = pd.DataFrame(rows).dropna()

print("TOPLAM EĞİTİM SATIRI:", len(data))

X = data.drop("target", axis=1)
y = data["target"]

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=8,
    random_state=42
)

model.fit(X, y)

joblib.dump(model, "model_nasdaq.pkl")

print("NASDAQ MODELİ v2 HAZIR")
