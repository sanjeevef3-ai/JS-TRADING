"""
Complete Candlestick Pattern Detection Engine
Checks for Single, Double, and Triple Japanese Candlestick Patterns.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np

def detect_candlestick_patterns(df: pd.DataFrame, lookback: int = 5) -> List[Dict[str, Any]]:
    """
    Detects candlestick patterns in the most recent candles of df.
    Returns list of detected patterns with bias, confidence, and description.
    """
    if df.empty or len(df) < 5:
        return []

    patterns = []
    
    # We analyze the last 'lookback' candles
    start_idx = max(3, len(df) - lookback)
    
    for i in range(start_idx, len(df)):
        c = df.iloc[i]        # Current candle
        p1 = df.iloc[i - 1]   # Previous candle
        p2 = df.iloc[i - 2]   # 2 candles ago
        
        # Dimensions for current candle
        c_open, c_high, c_low, c_close = c["Open"], c["High"], c["Low"], c["Close"]
        c_body = abs(c_close - c_open)
        c_range = max(c_high - c_low, 1e-6)
        c_upper_shadow = c_high - max(c_open, c_close)
        c_lower_shadow = min(c_open, c_close) - c_low
        is_bullish = c_close >= c_open
        is_bearish = c_close < c_open
        time_str = str(c["time"])
        
        # Dimensions for p1 candle
        p1_open, p1_high, p1_low, p1_close = p1["Open"], p1["High"], p1["Low"], p1["Close"]
        p1_body = abs(p1_close - p1_open)
        p1_range = max(p1_high - p1_low, 1e-6)
        p1_is_bullish = p1_close >= p1_open
        p1_is_bearish = p1_close < p1_open

        # Dimensions for p2 candle
        p2_open, p2_high, p2_low, p2_close = p2["Open"], p2["High"], p2["Low"], p2["Close"]
        p2_body = abs(p2_close - p2_open)
        p2_is_bearish = p2_close < p2_open
        p2_is_bullish = p2_close >= p2_open

        # --- 1. SINGLE CANDLE PATTERNS ---
        
        # Hammer (Bullish Reversal after downtrend)
        if c_lower_shadow >= 2 * c_body and c_upper_shadow <= 0.2 * c_range and c_body > 0.05 * c_range:
            if p1_close < p1_open: # Previous was red
                patterns.append({
                    "pattern": "Hammer",
                    "type": "Single Candlestick",
                    "bias": "Bullish",
                    "confidence": 82,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Long lower shadow shows strong buyer rejection of lower prices."
                })

        # Inverted Hammer (Bullish Reversal)
        if c_upper_shadow >= 2 * c_body and c_lower_shadow <= 0.2 * c_range and c_body > 0.05 * c_range:
            if p1_close < p1_open:
                patterns.append({
                    "pattern": "Inverted Hammer",
                    "type": "Single Candlestick",
                    "bias": "Bullish",
                    "confidence": 75,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Bulls pushed price high during session, signaling early buying accumulation."
                })

        # Shooting Star (Bearish Reversal after uptrend)
        if c_upper_shadow >= 2 * c_body and c_lower_shadow <= 0.2 * c_range and p1_is_bullish:
            patterns.append({
                "pattern": "Shooting Star",
                "type": "Single Candlestick",
                "bias": "Bearish",
                "confidence": 84,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Long upper wick shows rejection from highs by aggressive sellers."
            })

        # Hanging Man (Bearish Reversal at top)
        if c_lower_shadow >= 2 * c_body and c_upper_shadow <= 0.2 * c_range and p1_is_bullish and c_close > p1_close:
            patterns.append({
                "pattern": "Hanging Man",
                "type": "Single Candlestick",
                "bias": "Bearish",
                "confidence": 72,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Potential exhaustion of uptrend; sellers briefly dominated before close."
            })

        # Doji Patterns
        if c_body <= 0.08 * c_range:
            if c_lower_shadow >= 0.65 * c_range and c_upper_shadow <= 0.15 * c_range:
                patterns.append({
                    "pattern": "Dragonfly Doji",
                    "type": "Single Candlestick",
                    "bias": "Bullish",
                    "confidence": 80,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "High buying pressure off intraday lows, bullish reversal signal."
                })
            elif c_upper_shadow >= 0.65 * c_range and c_lower_shadow <= 0.15 * c_range:
                patterns.append({
                    "pattern": "Gravestone Doji",
                    "type": "Single Candlestick",
                    "bias": "Bearish",
                    "confidence": 80,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Severe rejection at top of session, bearish exhaustion signal."
                })
            else:
                patterns.append({
                    "pattern": "Neutral Doji",
                    "type": "Single Candlestick",
                    "bias": "Neutral",
                    "confidence": 65,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Complete indecision between buyers and sellers, impending breakout."
                })

        # Marubozu (Extreme directional impulse)
        if c_body >= 0.90 * c_range:
            if is_bullish:
                patterns.append({
                    "pattern": "Bullish Marubozu",
                    "type": "Single Candlestick",
                    "bias": "Bullish",
                    "confidence": 88,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Full solid green candle with no wicks. Overwhelming institutional buying."
                })
            else:
                patterns.append({
                    "pattern": "Bearish Marubozu",
                    "type": "Single Candlestick",
                    "bias": "Bearish",
                    "confidence": 88,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Full solid red candle with no wicks. Overwhelming institutional selling."
                })

        # --- 2. DOUBLE CANDLE PATTERNS ---

        # Bullish Engulfing
        if p1_is_bearish and is_bullish and c_close > p1_open and c_open < p1_close:
            patterns.append({
                "pattern": "Bullish Engulfing",
                "type": "Double Candlestick",
                "bias": "Bullish",
                "confidence": 89,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Green candle completely engulfs previous red candle body. Major bullish momentum."
            })

        # Bearish Engulfing
        if p1_is_bullish and is_bearish and c_close < p1_open and c_open > p1_close:
            patterns.append({
                "pattern": "Bearish Engulfing",
                "type": "Double Candlestick",
                "bias": "Bearish",
                "confidence": 89,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Red candle completely engulfs previous green candle body. Strong distribution."
            })

        # Piercing Line (Bullish)
        if p1_is_bearish and is_bullish and c_open < p1_low and c_close > (p1_open + p1_close) / 2 and c_close < p1_open:
            patterns.append({
                "pattern": "Piercing Line",
                "type": "Double Candlestick",
                "bias": "Bullish",
                "confidence": 78,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Gaps down and closes more than 50% into previous red body. Bullish revival."
            })

        # Dark Cloud Cover (Bearish)
        if p1_is_bullish and is_bearish and c_open > p1_high and c_close < (p1_open + p1_close) / 2 and c_close > p1_open:
            patterns.append({
                "pattern": "Dark Cloud Cover",
                "type": "Double Candlestick",
                "bias": "Bearish",
                "confidence": 78,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Gaps up then drops deep into prior green candle body. Bearish reversal."
            })

        # Bullish Harami & Bearish Harami
        if p1_body > 2 * c_body:
            if p1_is_bearish and is_bullish and c_open > p1_close and c_close < p1_open:
                patterns.append({
                    "pattern": "Bullish Harami",
                    "type": "Double Candlestick",
                    "bias": "Bullish",
                    "confidence": 74,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Small green candle contained inside previous large red body. Selling pause."
                })
            elif p1_is_bullish and is_bearish and c_open < p1_close and c_close > p1_open:
                patterns.append({
                    "pattern": "Bearish Harami",
                    "type": "Double Candlestick",
                    "bias": "Bearish",
                    "confidence": 74,
                    "candle_index": i,
                    "time": time_str,
                    "price": round(c_close, 2),
                    "desc": "Small red candle contained inside previous large green body. Buying exhaustion."
                })

        # Tweezer Bottom & Top
        if abs(c_low - p1_low) / max(c_low, 1e-6) < 0.001 and p1_is_bearish and is_bullish:
            patterns.append({
                "pattern": "Tweezer Bottom",
                "type": "Double Candlestick",
                "bias": "Bullish",
                "confidence": 80,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Equal lows formed across consecutive candles showing rock-solid support."
            })
        if abs(c_high - p1_high) / max(c_high, 1e-6) < 0.001 and p1_is_bullish and is_bearish:
            patterns.append({
                "pattern": "Tweezer Top",
                "type": "Double Candlestick",
                "bias": "Bearish",
                "confidence": 80,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Equal highs formed across consecutive candles indicating immovable resistance."
            })

        # --- 3. TRIPLE CANDLE PATTERNS ---

        # Morning Star (Bullish Reversal)
        if p2_is_bearish and p1_body < 0.3 * p2_body and is_bullish and c_close > (p2_open + p2_close) / 2:
            patterns.append({
                "pattern": "Morning Star",
                "type": "Triple Candlestick",
                "bias": "Bullish",
                "confidence": 91,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "High probability 3-candle bottom reversal confirming shift from bear to bull."
            })

        # Evening Star (Bearish Reversal)
        if p2_is_bullish and p1_body < 0.3 * p2_body and is_bearish and c_close < (p2_open + p2_close) / 2:
            patterns.append({
                "pattern": "Evening Star",
                "type": "Triple Candlestick",
                "bias": "Bearish",
                "confidence": 91,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "High probability 3-candle top reversal confirming aggressive bull trap."
            })

        # Three White Soldiers
        if p2_is_bullish and p1_is_bullish and is_bullish and (c_close > p1_close > p2_close) and (c_open > p1_open > p2_open):
            patterns.append({
                "pattern": "Three White Soldiers",
                "type": "Triple Candlestick",
                "bias": "Bullish",
                "confidence": 87,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Three successive long green candles with higher highs and closes. Strong trend continuation."
            })

        # Three Black Crows
        if p2_is_bearish and p1_is_bearish and is_bearish and (c_close < p1_close < p2_close) and (c_open < p1_open < p2_open):
            patterns.append({
                "pattern": "Three Black Crows",
                "type": "Triple Candlestick",
                "bias": "Bearish",
                "confidence": 87,
                "candle_index": i,
                "time": time_str,
                "price": round(c_close, 2),
                "desc": "Three successive long red candles with lower lows and closes. Strong downtrend continuation."
            })

    return patterns
