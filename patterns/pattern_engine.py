"""
Comprehensive Pattern Scanner and Aggregator Engine
Ensures NO pattern is missed across all active timeframes (5m, 15m, 1h, 1D).
"""

from typing import Dict, Any, List
import pandas as pd
from .candlestick import detect_candlestick_patterns
from .chart_patterns import detect_classical_patterns

def scan_all_patterns(timeframes_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Scans candlestick and classical chart patterns across all timeframes.
    Returns structured results by timeframe and consolidated pattern radar.
    """
    results_by_tf = {}
    all_patterns_flat = []

    total_bullish_weight = 0
    total_bearish_weight = 0

    for tf, df in timeframes_data.items():
        if df.empty or len(df) < 5:
            results_by_tf[tf] = {"candlestick": [], "classical": []}
            continue

        c_patterns = detect_candlestick_patterns(df)
        g_patterns = detect_classical_patterns(df)

        # Tag timeframe on each pattern
        for p in c_patterns:
            p["timeframe"] = tf
            all_patterns_flat.append(p)
            weight = p.get("confidence", 70)
            if p["bias"] == "Bullish":
                total_bullish_weight += weight
            elif p["bias"] == "Bearish":
                total_bearish_weight += weight

        for p in g_patterns:
            p["timeframe"] = tf
            all_patterns_flat.append(p)
            weight = p.get("confidence", 75) * 1.25 # Classical patterns carry higher weight
            if p["bias"] == "Bullish":
                total_bullish_weight += weight
            elif p["bias"] == "Bearish":
                total_bearish_weight += weight

        results_by_tf[tf] = {
            "candlestick": c_patterns,
            "classical": g_patterns,
            "count": len(c_patterns) + len(g_patterns)
        }

    # Consolidated Pattern Radar Bias
    total_score = total_bullish_weight + total_bearish_weight
    if total_score > 0:
        bullish_pct = round((total_bullish_weight / total_score) * 100, 1)
        bearish_pct = round((total_bearish_weight / total_score) * 100, 1)
    else:
        bullish_pct, bearish_pct = 50.0, 50.0

    if bullish_pct > 65:
        primary_bias = "Strong Bullish"
    elif bullish_pct > 55:
        primary_bias = "Mild Bullish"
    elif bearish_pct > 65:
        primary_bias = "Strong Bearish"
    elif bearish_pct > 55:
        primary_bias = "Mild Bearish"
    else:
        primary_bias = "Neutral / Sideways Indecision"

    return {
        "by_timeframe": results_by_tf,
        "all_detected_patterns": all_patterns_flat,
        "total_patterns_detected": len(all_patterns_flat),
        "pattern_bias": primary_bias,
        "bullish_strength_pct": bullish_pct,
        "bearish_strength_pct": bearish_pct
    }
