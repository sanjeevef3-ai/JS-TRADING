"""
Divergence Detection Engine (RSI & MACD)
Detects Regular and Hidden Bullish and Bearish Divergences across price swings.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def detect_divergences(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detects Regular and Hidden Divergences between Price and RSI(14).
    """
    if df.empty or len(df) < 30:
        return []

    close = df["Close"].values
    n = len(close)

    # Compute RSI
    deltas = np.diff(close)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.zeros(n)
    avg_loss = np.zeros(n)
    avg_gain[14] = np.mean(gains[:14])
    avg_loss[14] = np.mean(losses[:14])
    for i in range(15, n):
        avg_gain[i] = (avg_gain[i - 1] * 13 + gains[i - 1]) / 14
        avg_loss[i] = (avg_loss[i - 1] * 13 + losses[i - 1]) / 14

    rs = np.divide(avg_gain[14:], avg_loss[14:], out=np.zeros_like(avg_gain[14:]), where=avg_loss[14:] != 0)
    rsi_full = np.pad(100 - (100 / (1 + rs)), (14, 0), mode='edge')

    divergences = []

    # Find peaks and troughs in price
    price_peaks, _ = find_peaks(close, distance=5, prominence=0.005 * np.mean(close))
    price_troughs, _ = find_peaks(-close, distance=5, prominence=0.005 * np.mean(close))

    # 1. Bearish Divergences (Compare peaks in price vs RSI)
    if len(price_peaks) >= 2:
        p1, p2 = price_peaks[-2], price_peaks[-1]
        price1, price2 = close[p1], close[p2]
        rsi1, rsi2 = rsi_full[p1], rsi_full[p2]

        # Regular Bearish Divergence: Higher High in Price, Lower High in RSI
        if price2 > price1 and rsi2 < rsi1:
            divergences.append({
                "type": "Regular Bearish Divergence",
                "indicator": "RSI",
                "bias": "Bearish Reversal",
                "confidence": 86,
                "price_swing": f"{round(price1, 2)} -> {round(price2, 2)} (Higher High)",
                "rsi_swing": f"{round(rsi1, 1)} -> {round(rsi2, 1)} (Lower High)",
                "desc": "Price made Higher High but momentum made Lower High. Severe upward exhaustion."
            })

        # Hidden Bearish Divergence: Lower High in Price, Higher High in RSI
        elif price2 < price1 and rsi2 > rsi1:
            divergences.append({
                "type": "Hidden Bearish Divergence",
                "indicator": "RSI",
                "bias": "Bearish Continuation",
                "confidence": 80,
                "price_swing": f"{round(price1, 2)} -> {round(price2, 2)} (Lower High)",
                "rsi_swing": f"{round(rsi1, 1)} -> {round(rsi2, 1)} (Higher High)",
                "desc": "Downtrend continuation signal: Price failed to reach previous high despite stronger RSI push."
            })

    # 2. Bullish Divergences (Compare troughs in price vs RSI)
    if len(price_troughs) >= 2:
        t1, t2 = price_troughs[-2], price_troughs[-1]
        price1, price2 = close[t1], close[t2]
        rsi1, rsi2 = rsi_full[t1], rsi_full[t2]

        # Regular Bullish Divergence: Lower Low in Price, Higher Low in RSI
        if price2 < price1 and rsi2 > rsi1:
            divergences.append({
                "type": "Regular Bullish Divergence",
                "indicator": "RSI",
                "bias": "Bullish Reversal",
                "confidence": 86,
                "price_swing": f"{round(price1, 2)} -> {round(price2, 2)} (Lower Low)",
                "rsi_swing": f"{round(rsi1, 1)} -> {round(rsi2, 1)} (Higher Low)",
                "desc": "Price made Lower Low but selling momentum dried up, forming Higher Low in RSI."
            })

        # Hidden Bullish Divergence: Higher Low in Price, Lower Low in RSI
        elif price2 > price1 and rsi2 < rsi1:
            divergences.append({
                "type": "Hidden Bullish Divergence",
                "indicator": "RSI",
                "bias": "Bullish Continuation",
                "confidence": 80,
                "price_swing": f"{round(price1, 2)} -> {round(price2, 2)} (Higher Low)",
                "rsi_swing": f"{round(rsi1, 1)} -> {round(rsi2, 1)} (Lower Low)",
                "desc": "Uptrend continuation signal: Price held a higher low despite deep RSI reset."
            })

    return divergences
