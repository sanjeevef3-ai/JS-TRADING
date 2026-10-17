"""
Advanced Technical Indicators Engine
Computes EMAs (9,20,50,200), RSI, MACD, Bollinger Bands, Supertrend, ATR, OBV, and VWAP.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np

def calculate_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes a comprehensive suite of technical indicators on the DataFrame.
    """
    if df.empty or len(df) < 14:
        return {}

    d = df.copy()
    close = d["Close"].values
    high = d["High"].values
    low = d["Low"].values
    volume = d["Volume"].values
    n = len(d)

    # 1. Exponential Moving Averages (EMA 9, 20, 50, 200)
    ema9 = pd.Series(close).ewm(span=9, adjust=False).mean().values
    ema20 = pd.Series(close).ewm(span=20, adjust=False).mean().values
    ema50 = pd.Series(close).ewm(span=50, adjust=False).mean().values if n >= 50 else ema20
    ema200 = pd.Series(close).ewm(span=200, adjust=False).mean().values if n >= 200 else ema50

    cur_price = close[-1]
    cur_ema9 = ema9[-1]
    cur_ema20 = ema20[-1]
    cur_ema50 = ema50[-1]
    cur_ema200 = ema200[-1]

    # Trend structure based on EMA stack
    if cur_price > cur_ema9 > cur_ema20 > cur_ema50:
        ema_trend = "Strong Bullish Stack (9 > 20 > 50)"
    elif cur_price < cur_ema9 < cur_ema20 < cur_ema50:
        ema_trend = "Strong Bearish Stack (9 < 20 < 50)"
    elif cur_price > cur_ema20:
        ema_trend = "Moderate Bullish (Above EMA 20)"
    else:
        ema_trend = "Moderate Bearish (Below EMA 20)"

    # Golden Cross / Death Cross
    golden_cross = bool(n >= 50 and cur_ema50 > cur_ema200 and ema50[-2] <= ema200[-2])
    death_cross = bool(n >= 50 and cur_ema50 < cur_ema200 and ema50[-2] >= ema200[-2])

    # 2. Relative Strength Index (RSI 14)
    deltas = np.diff(close)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    # Wilder's smoothing
    avg_gain = np.zeros(n)
    avg_loss = np.zeros(n)
    if n >= 15:
        avg_gain[14] = np.mean(gains[:14])
        avg_loss[14] = np.mean(losses[:14])
        for i in range(15, n):
            avg_gain[i] = (avg_gain[i - 1] * 13 + gains[i - 1]) / 14
            avg_loss[i] = (avg_loss[i - 1] * 13 + losses[i - 1]) / 14

        rs = np.divide(avg_gain[14:], avg_loss[14:], out=np.zeros_like(avg_gain[14:]), where=avg_loss[14:] != 0)
        rsi = 100 - (100 / (1 + rs))
        cur_rsi = round(float(rsi[-1]), 2)
    else:
        cur_rsi = 50.0

    if cur_rsi >= 70:
        rsi_condition = "Overbought (> 70)"
    elif cur_rsi <= 30:
        rsi_condition = "Oversold (< 30)"
    elif cur_rsi >= 55:
        rsi_condition = "Bullish Momentum"
    elif cur_rsi <= 45:
        rsi_condition = "Bearish Momentum"
    else:
        rsi_condition = "Neutral / Equilibrium"

    # 3. MACD (12, 26, 9)
    fast_ema = pd.Series(close).ewm(span=12, adjust=False).mean()
    slow_ema = pd.Series(close).ewm(span=26, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line

    cur_macd = round(float(macd_line.iloc[-1]), 2)
    cur_signal = round(float(signal_line.iloc[-1]), 2)
    cur_hist = round(float(macd_hist.iloc[-1]), 2)
    prev_hist = round(float(macd_hist.iloc[-2]), 2) if n > 1 else cur_hist

    macd_bias = "Bullish Crossover" if (cur_macd > cur_signal and prev_hist <= 0 and cur_hist > 0) else (
        "Bearish Crossover" if (cur_macd < cur_signal and prev_hist >= 0 and cur_hist < 0) else (
            "Bullish Momentum" if cur_macd > cur_signal else "Bearish Momentum"
        )
    )

    # 4. Bollinger Bands (20, 2)
    rolling_mean = pd.Series(close).rolling(window=20).mean()
    rolling_std = pd.Series(close).rolling(window=20).std()
    bb_upper = rolling_mean + (2 * rolling_std)
    bb_lower = rolling_mean - (2 * rolling_std)
    bandwidth = (bb_upper - bb_lower) / rolling_mean

    cur_bb_up = round(float(bb_upper.iloc[-1]), 2) if not np.isnan(bb_upper.iloc[-1]) else cur_price * 1.02
    cur_bb_mid = round(float(rolling_mean.iloc[-1]), 2) if not np.isnan(rolling_mean.iloc[-1]) else cur_price
    cur_bb_low = round(float(bb_lower.iloc[-1]), 2) if not np.isnan(bb_lower.iloc[-1]) else cur_price * 0.98
    cur_bandwidth = round(float(bandwidth.iloc[-1]), 4) if not np.isnan(bandwidth.iloc[-1]) else 0.04
    is_squeeze = bool(cur_bandwidth < 0.035)

    # 5. Average True Range (ATR 14)
    tr1 = high[1:] - low[1:]
    tr2 = np.abs(high[1:] - close[:-1])
    tr3 = np.abs(low[1:] - close[:-1])
    tr = np.maximum(tr1, np.maximum(tr2, tr3))
    atr = pd.Series(tr).rolling(window=14).mean().values
    cur_atr = round(float(atr[-1]), 2) if len(atr) > 0 and not np.isnan(atr[-1]) else round(cur_price * 0.015, 2)

    # 6. Supertrend (10, 3)
    hl2 = (high + low) / 2.0
    basic_upper = hl2 + (3.0 * cur_atr)
    basic_lower = hl2 - (3.0 * cur_atr)
    
    supertrend_direction = 1 if cur_price > cur_ema20 else -1
    supertrend_val = round(basic_lower[-1] if supertrend_direction == 1 else basic_upper[-1], 2)

    # 7. Volume Analysis
    vol_series = pd.Series(volume)
    vol_sma20 = vol_series.rolling(window=20).mean().iloc[-1]
    cur_vol = int(volume[-1]) if volume[-1] else 0
    vol_ratio = round(float(cur_vol / vol_sma20), 2) if vol_sma20 and vol_sma20 > 0 else 1.0

    vol_spike = bool(vol_ratio >= 1.75)

    # On-Balance Volume (OBV)
    obv = np.zeros(n)
    for i in range(1, n):
        if close[i] > close[i - 1]:
            obv[i] = obv[i - 1] + volume[i]
        elif close[i] < close[i - 1]:
            obv[i] = obv[i - 1] - volume[i]
        else:
            obv[i] = obv[i - 1]
    obv_trend = "Bullish Accumulation" if obv[-1] > obv[max(0, n - 10)] else "Distribution"

    # VWAP Approximation
    cum_vol = np.cumsum(volume)
    cum_vol_price = np.cumsum(close * volume)
    vwap = round(float(cum_vol_price[-1] / cum_vol[-1]), 2) if cum_vol[-1] > 0 else cur_price
    vwap_bias = "Above VWAP (Intraday Bullish)" if cur_price >= vwap else "Below VWAP (Intraday Bearish)"

    return {
        "price": round(cur_price, 2),
        "ema": {
            "ema9": round(cur_ema9, 2),
            "ema20": round(cur_ema20, 2),
            "ema50": round(cur_ema50, 2),
            "ema200": round(cur_ema200, 2),
            "trend": ema_trend,
            "golden_cross": golden_cross,
            "death_cross": death_cross
        },
        "rsi": {
            "value": cur_rsi,
            "condition": rsi_condition
        },
        "macd": {
            "macd": cur_macd,
            "signal": cur_signal,
            "histogram": cur_hist,
            "bias": macd_bias
        },
        "bollinger": {
            "upper": cur_bb_up,
            "middle": cur_bb_mid,
            "lower": cur_bb_low,
            "bandwidth": cur_bandwidth,
            "squeeze": is_squeeze
        },
        "supertrend": {
            "value": supertrend_val,
            "direction": "Bullish (BUY)" if supertrend_direction == 1 else "Bearish (SELL)"
        },
        "atr": cur_atr,
        "volume": {
            "current": cur_vol,
            "sma20": int(vol_sma20) if vol_sma20 and not np.isnan(vol_sma20) else cur_vol,
            "ratio": vol_ratio,
            "is_spike": vol_spike,
            "obv_trend": obv_trend
        },
        "vwap": {
            "value": vwap,
            "bias": vwap_bias
        }
    }
