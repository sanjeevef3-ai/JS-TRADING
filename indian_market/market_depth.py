"""
Market Depth, Pivots, Support & Resistance, and Fibonacci Levels
Specially tuned for Indian Stock Market Intraday & Swing traders.
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np

def calculate_pivots(high: float, low: float, close: float) -> Dict[str, Any]:
    """
    Computes both Standard Floor Pivots and Camarilla Pivots.
    """
    # 1. Standard Floor Pivots
    pp = (high + low + close) / 3.0
    r1 = (2 * pp) - low
    s1 = (2 * pp) - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    r3 = high + 2 * (pp - low)
    s3 = low - 2 * (high - pp)

    # 2. Camarilla Pivots (widely used in NSE intraday trading)
    diff = high - low
    h4 = close + (diff * 1.1 / 2.0)  # Long breakout level
    h3 = close + (diff * 1.1 / 4.0)  # Reversal short level
    l3 = close - (diff * 1.1 / 4.0)  # Reversal long level
    l4 = close - (diff * 1.1 / 2.0)  # Short breakdown level

    return {
        "standard": {
            "r3": round(r3, 2),
            "r2": round(r2, 2),
            "r1": round(r1, 2),
            "pivot": round(pp, 2),
            "s1": round(s1, 2),
            "s2": round(s2, 2),
            "s3": round(s3, 2)
        },
        "camarilla": {
            "breakout_long_h4": round(h4, 2),
            "resistance_h3": round(h3, 2),
            "support_l3": round(l3, 2),
            "breakdown_short_l4": round(l4, 2)
        }
    }

def calculate_fibonacci(high: float, low: float, is_uptrend: bool = True) -> Dict[str, float]:
    """
    Computes Fibonacci Retracement and Extension levels from swing high & low.
    """
    diff = high - low
    if diff <= 0:
        return {}

    if is_uptrend:
        return {
            "0.0% (Swing Low)": round(low, 2),
            "23.6%": round(high - 0.764 * diff, 2),
            "38.2%": round(high - 0.618 * diff, 2),
            "50.0% (Equilibrium)": round(high - 0.500 * diff, 2),
            "61.8% (Golden Pocket)": round(high - 0.382 * diff, 2),
            "78.6%": round(high - 0.214 * diff, 2),
            "100.0% (Swing High)": round(high, 2),
            "127.2% Ext": round(high + 0.272 * diff, 2),
            "161.8% Ext": round(high + 0.618 * diff, 2)
        }
    else:
        return {
            "0.0% (Swing High)": round(high, 2),
            "23.6%": round(low + 0.764 * diff, 2),
            "38.2%": round(low + 0.618 * diff, 2),
            "50.0% (Equilibrium)": round(low + 0.500 * diff, 2),
            "61.8% (Golden Pocket)": round(low + 0.382 * diff, 2),
            "78.6%": round(low + 0.214 * diff, 2),
            "100.0% (Swing Low)": round(low, 2),
            "127.2% Ext": round(low - 0.272 * diff, 2),
            "161.8% Ext": round(low - 0.618 * diff, 2)
        }

def calculate_support_resistance(df: pd.DataFrame, num_levels: int = 3) -> Dict[str, List[float]]:
    """
    Finds dynamic major support and resistance zones based on price cluster density.
    """
    if df.empty or len(df) < 15:
        return {"supports": [], "resistances": []}

    current_price = df["Close"].iloc[-1]
    highs = df["High"].values
    lows = df["Low"].values

    # Find swing highs and swing lows (local extrema)
    swing_highs = []
    swing_lows = []

    for i in range(2, len(df) - 2):
        if highs[i] > highs[i - 1] and highs[i] > highs[i - 2] and highs[i] > highs[i + 1] and highs[i] > highs[i + 2]:
            swing_highs.append(highs[i])
        if lows[i] < lows[i - 1] and lows[i] < lows[i - 2] and lows[i] < lows[i + 1] and lows[i] < lows[i + 2]:
            swing_lows.append(lows[i])

    # Cluster within 0.7% tolerance
    def cluster_levels(levels):
        if not levels:
            return []
        levels.sort()
        clustered = []
        cur_cluster = [levels[0]]
        for l in levels[1:]:
            if (l - cur_cluster[-1]) / cur_cluster[-1] < 0.012:
                cur_cluster.append(l)
            else:
                clustered.append(float(np.mean(cur_cluster)))
                cur_cluster = [l]
        clustered.append(float(np.mean(cur_cluster)))
        return clustered

    c_highs = cluster_levels(swing_highs)
    c_lows = cluster_levels(swing_lows)

    resistances = [round(r, 2) for r in c_highs if r > current_price]
    supports = [round(s, 2) for s in c_lows if s < current_price]

    resistances = sorted(resistances)[:num_levels]
    supports = sorted(supports, reverse=True)[:num_levels]

    return {
        "supports": supports,
        "resistances": resistances
    }
