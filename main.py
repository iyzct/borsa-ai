from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import joblib
import numpy as np
import os
import traceback

# MODELLER
try:
    model_bist = joblib.load("model_bist.pkl")
    print("MODEL BIST LOADED")
except Exception as e:
    print("MODEL BIST ERROR:")
    traceback.print_exc()
    model_bist = None

try:
    model_us = joblib.load("model_nasdaq.pkl")
    print("MODEL NASDAQ LOADED")
except Exception as e:
    print("MODEL NASDAQ ERROR:")
    traceback.print_exc()
    model_us = None
app = FastAPI(title="Nasdaq/Bist AI", version="1.0")
print("FILES:", os.listdir())

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React'ten gelen istekler için
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------- REQUEST MODEL -----------
class AnalyzeRequest(BaseModel):
    ticker: str
    market: str  # BIST / US


# ----------- BIST ANALYSIS -----------
def analyze_bist(ticker: str):

    if model_bist is None:
        return {"error": "Model not loaded"}
    
    df = yf.download(ticker, period="5y")

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty:
        return {"error": "Veri bulunamadı"}

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()
    df["momentum"] = df["Close"] / df["Close"].shift(20) - 1
    df["volume_change"] = df["Volume"] / df["Volume"].shift(20) - 1

    # 🔴 Infinity temizleme
    df = df.replace([np.inf, -np.inf], np.nan)

    df = df.dropna()

    latest = df.iloc[-1]

    X = pd.DataFrame([{
        "ma20": latest["ma20"],
        "ma50": latest["ma50"],
        "momentum": latest["momentum"],
        "volume_change": latest["volume_change"]
    }])

    proba = model_bist.predict_proba(X)[0]
    confidence = int(proba[1] * 100)

    decision = "AL" if confidence >= 60 else "SAT / BEKLE"

    up = int(proba[1] * 100)
    down = int(proba[0] * 100)


    return {
        "ticker": ticker,
        "up": up,
        "down": down
    }   


# ----------- US ANALYSIS -----------
def analyze_us(ticker: str):

    if model_us is None:
        return {"error": "Model not loaded"}

    t = yf.Ticker(ticker)
    df = t.history(period="5y")

    if df.empty:
        return {"error": "Veri bulunamadı"}

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()
    df = df.dropna()

    info = t.info
    fields = ["profitMargins", "debtToEquity", "trailingPE", "revenueGrowth"]

    if any(info.get(f) is None for f in fields):
        return {"error": "Bilanço eksik"}

    latest = df.iloc[-1]

    X = pd.DataFrame([{
        "ma20": latest["ma20"].item(),
        "ma50": latest["ma50"].item(),
        "profit_margin": info["profitMargins"],
        "debt_to_equity": info["debtToEquity"],
        "pe": info["trailingPE"],
        "revenue_growth": info["revenueGrowth"]
    }])

    proba = model_us.predict_proba(X)[0]
    up = int(proba[1] * 100)
    down = int(proba[0] * 100)


    return {
        "ticker": ticker,
        "up": up,
        "down": down
    }   


# ----------- API ENDPOINT -----------
@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    ticker = req.ticker.upper()
    market = req.market.upper()

    if market == "BIST":
        if not ticker.endswith(".IS"):
            ticker += ".IS"
        return analyze_bist(ticker)

    return analyze_us(ticker)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": "1.0"}
