"""
Multi-Timeframe Market Data Fetcher for Indian Equities and Indices
Fetches 5m, 15m, 1h, and 1D data with robust fallback handling and IST timestamps.
"""

import time
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
import yfinance as yf
from config import SUPPORTED_TIMEFRAMES, TIMEFRAME_PERIODS
from .symbol_resolver import resolve_symbol

class MarketDataFetcher:
    """Fetches and prepares market data for Indian Stocks and Indices."""
    
    def __init__(self, cache_ttl_seconds: int = 45):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = cache_ttl_seconds
        
    def get_live_quote(self, ticker: str) -> Dict[str, Any]:
        """Fetch real-time snapshot of the given ticker."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.fast_info
            
            # Fast info fields
            last_price = getattr(info, "last_price", None)
            prev_close = getattr(info, "previous_close", None)
            open_price = getattr(info, "open", None)
            day_high = getattr(info, "day_high", None)
            day_low = getattr(info, "day_low", None)
            volume = getattr(info, "last_volume", None)
            year_high = getattr(info, "year_high", None)
            year_low = getattr(info, "year_low", None)
            
            # Fallback to recent 1-day candle if fast_info missing
            if last_price is None or np.isnan(last_price):
                hist = stock.history(period="5d", interval="1d")
                if not hist.empty:
                    last_price = float(hist["Close"].iloc[-1])
                    prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else float(hist["Open"].iloc[-1])
                    open_price = float(hist["Open"].iloc[-1])
                    day_high = float(hist["High"].iloc[-1])
                    day_low = float(hist["Low"].iloc[-1])
                    volume = int(hist["Volume"].iloc[-1])
            
            if last_price is None:
                return {}
                
            change = (last_price - prev_close) if prev_close else 0.0
            p_change = ((change / prev_close) * 100) if prev_close else 0.0
            
            return {
                "ticker": ticker,
                "current_price": round(float(last_price), 2),
                "previous_close": round(float(prev_close), 2) if prev_close else None,
                "open": round(float(open_price), 2) if open_price else None,
                "high": round(float(day_high), 2) if day_high else None,
                "low": round(float(day_low), 2) if day_low else None,
                "change": round(float(change), 2),
                "p_change": round(float(p_change), 2),
                "volume": int(volume) if volume and not np.isnan(volume) else 0,
                "52w_high": round(float(year_high), 2) if year_high else None,
                "52w_low": round(float(year_low), 2) if year_low else None,
                "timestamp": time.time()
            }
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}

    def fetch_timeframe_candles(self, ticker: str, interval: str) -> pd.DataFrame:
        """Fetch candles for specific timeframe with standard OHLCV columns."""
        period = TIMEFRAME_PERIODS.get(interval, "1mo")
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            if df.empty:
                # Fallback period if requested period failed
                df = stock.history(period="max" if interval == "1d" else "5d", interval=interval)
                
            if df.empty:
                return pd.DataFrame()
                
            # Clean columns
            df = df.reset_index()
            # Standardize date column
            date_col = "Datetime" if "Datetime" in df.columns else "Date"
            df["timestamp"] = pd.to_datetime(df[date_col])
            
            # Format to IST string
            try:
                if df["timestamp"].dt.tz is not None:
                    df["timestamp_ist"] = df["timestamp"].dt.tz_convert("Asia/Kolkata").dt.strftime("%Y-%m-%d %H:%M")
                else:
                    df["timestamp_ist"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                df["timestamp_ist"] = df["timestamp"].astype(str)
                
            cols = ["timestamp_ist", "Open", "High", "Low", "Close", "Volume"]
            df = df[cols].rename(columns={"timestamp_ist": "time"})
            # Drop NaN or 0 close
            df = df.dropna(subset=["Close"])
            df = df[df["Close"] > 0].reset_index(drop=True)
            return df
        except Exception as e:
            print(f"[Error fetching {ticker} {interval}]: {e}")
            return pd.DataFrame()

    def fetch_multi_timeframe(self, user_query: str) -> Dict[str, Any]:
        """
        Main entry point: Resolves symbol, fetches live quote, and retrieves
        5m, 15m, 1h, 1D data concurrently.
        """
        clean_name, ticker = resolve_symbol(user_query)
        cache_key = f"{ticker}_all_mtf"
        
        now = time.time()
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if now - entry["timestamp"] < self.cache_ttl:
                return entry["data"]

        live_quote = self.get_live_quote(ticker)
        
        timeframes_data = {}
        for tf in SUPPORTED_TIMEFRAMES:
            df = self.fetch_timeframe_candles(ticker, tf)
            timeframes_data[tf] = df

        result = {
            "symbol": clean_name,
            "ticker": ticker,
            "live_quote": live_quote,
            "timeframes": timeframes_data,
            "fetched_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        self.cache[cache_key] = {
            "timestamp": now,
            "data": result
        }
        return result
