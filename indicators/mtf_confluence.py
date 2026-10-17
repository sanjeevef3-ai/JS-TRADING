"""
Multi-Timeframe Confluence Engine (5m, 15m, 1h, 1D)
Determines multi-timeframe directional agreement, pullback vs trend reversals, and confluence score.
"""

from typing import Dict, Any
import pandas as pd
from .technical import calculate_indicators

def analyze_mtf_confluence(timeframes_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Analyzes trend and momentum across all timeframes to produce a confluence matrix.
    """
    tf_scores = {}
    tf_details = {}

    # Weight assigned to each timeframe: Daily and 1h carry higher institutional weight
    weights = {
        "5m": 0.15,   # Micro entry timing
        "15m": 0.25,  # Intraday structure
        "1h": 0.30,   # Swing trend
        "1d": 0.30    # Institutional macro trend
    }

    weighted_confluence_sum = 0.0
    active_weight_sum = 0.0

    for tf, df in timeframes_data.items():
        if df.empty or len(df) < 14:
            tf_details[tf] = {"trend": "Insufficient Data", "score": 0}
            continue

        ind = calculate_indicators(df)
        if not ind:
            continue

        cur_price = ind["price"]
        ema20 = ind["ema"]["ema20"]
        ema50 = ind["ema"]["ema50"]
        rsi_val = ind["rsi"]["value"]
        macd_hist = ind["macd"]["histogram"]
        supertrend_dir = ind["supertrend"]["direction"]

        # Calculate TF directional score (-100 to +100)
        score = 0

        # Price vs EMA20
        if cur_price > ema20:
            score += 25
        else:
            score -= 25

        # EMA20 vs EMA50
        if ema20 > ema50:
            score += 25
        else:
            score -= 25

        # Supertrend
        if "BUY" in supertrend_dir:
            score += 25
        else:
            score -= 25

        # RSI Momentum
        if rsi_val > 55:
            score += 15
        elif rsi_val < 45:
            score -= 15

        # MACD histogram
        if macd_hist > 0:
            score += 10
        else:
            score -= 10

        # Bound score between -100 and +100
        score = max(-100, min(100, score))

        if score >= 50:
            bias = "Bullish"
        elif score <= -50:
            bias = "Bearish"
        else:
            bias = "Neutral / Consolidating"

        tf_scores[tf] = score
        tf_details[tf] = {
            "bias": bias,
            "score": score,
            "rsi": rsi_val,
            "price": cur_price,
            "ema20": ema20,
            "supertrend": supertrend_dir
        }

        w = weights.get(tf, 0.20)
        weighted_confluence_sum += score * w
        active_weight_sum += w

    overall_confluence_score = round(weighted_confluence_sum / active_weight_sum, 1) if active_weight_sum > 0 else 0

    # Determine Multi-Timeframe Alignment State
    is_macro_bull = tf_scores.get("1d", 0) > 20
    is_macro_bear = tf_scores.get("1d", 0) < -20
    is_micro_bull = tf_scores.get("5m", 0) > 20
    is_micro_bear = tf_scores.get("5m", 0) < -20

    if overall_confluence_score >= 60:
        confluence_state = "Full Bullish Confluence (High Conviction Long)"
        action_recommendation = "Aggressive Buy / Ride Breakouts with trailing stop"
    elif overall_confluence_score <= -60:
        confluence_state = "Full Bearish Confluence (High Conviction Short)"
        action_recommendation = "Aggressive Sell / Short Breakdowns"
    elif is_macro_bull and is_micro_bear:
        confluence_state = "Intraday Pullback in Macro Uptrend (Dip Buying Zone)"
        action_recommendation = "Look for reversal candlestick (Hammer/Engulfing) to BUY the dip"
    elif is_macro_bear and is_micro_bull:
        confluence_state = "Intraday Relief Bounce in Macro Downtrend (Sell on Rise)"
        action_recommendation = "Look for reversal candlestick (Shooting Star) to SELL the rally"
    else:
        confluence_state = "Mixed / Conflicted Timeframes (Range-Bound / Chop)"
        action_recommendation = "Trade strict support/resistance boundaries or wait for clarity"

    return {
        "confluence_score": overall_confluence_score,
        "confluence_state": confluence_state,
        "action_recommendation": action_recommendation,
        "timeframe_breakdown": tf_details
    }
