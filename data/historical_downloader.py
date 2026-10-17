"""
Historical Multi-Year Dataset Downloader & Archiver for NIFTY & Indian Stocks
Downloads 10-year daily and maximum intraday candle archives into data/historical/
"""

import os
from pathlib import Path
import yfinance as yf
import pandas as pd
from config import DATA_DIR

HISTORICAL_DIR = DATA_DIR / "historical"
HISTORICAL_DIR.mkdir(parents=True, exist_ok=True)

def download_historical_datasets():
    """
    Downloads and caches multi-year daily and intraday datasets for NIFTY and BANKNIFTY.
    """
    print("[Historical Downloader] Archiving multi-year Indian market data...")
    targets = [
        {"ticker": "^NSEI", "name": "nifty_10y_daily.csv", "period": "10y", "interval": "1d"},
        {"ticker": "^NSEBANK", "name": "banknifty_10y_daily.csv", "period": "10y", "interval": "1d"},
        {"ticker": "^NSEI", "name": "nifty_intraday_1h.csv", "period": "2y", "interval": "1h"},
        {"ticker": "^NSEI", "name": "nifty_intraday_15m.csv", "period": "60d", "interval": "15m"},
        {"ticker": "^NSEI", "name": "nifty_intraday_5m.csv", "period": "60d", "interval": "5m"}
    ]

    saved_files = []
    for t in targets:
        file_path = HISTORICAL_DIR / t["name"]
        print(f" -> Downloading {t['ticker']} ({t['period']}, {t['interval']})...")
        try:
            stk = yf.Ticker(t["ticker"])
            df = stk.history(period=t["period"], interval=t["interval"])
            if not df.empty:
                df = df.reset_index()
                df.to_csv(file_path, index=False)
                saved_files.append({
                    "file": t["name"],
                    "rows": len(df),
                    "start": str(df.iloc[0][df.columns[0]])[:10],
                    "end": str(df.iloc[-1][df.columns[0]])[:10]
                })
                print(f"    Saved {len(df)} candles to {file_path.name}")
        except Exception as e:
            print(f"    Error downloading {t['name']}: {e}")

    return {
        "status": "COMPLETED",
        "archive_dir": str(HISTORICAL_DIR),
        "total_datasets": len(saved_files),
        "details": saved_files
    }

if __name__ == "__main__":
    res = download_historical_datasets()
    print("Download Summary:", res)
