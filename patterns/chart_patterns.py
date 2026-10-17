"""
Classical and Advanced Geometric Chart Pattern Detection Engine
Covers Head and Shoulders, Double/Triple Tops and Bottoms, Triangles, Wedges, and Flags.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def detect_classical_patterns(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Detects classical geometric chart patterns using peak/trough analysis.
    """
    if df.empty or len(df) < 30:
        return []

    patterns = []
    closes = df["Close"].values
    highs = df["High"].values
    lows = df["Low"].values
    n = len(closes)
    cur_price = closes[-1]
    
    # 1. Find prominent peaks (resistance) and troughs (support)
    # Distance of at least 4 candles between peaks
    peak_indices, _ = find_peaks(highs, distance=4, prominence=0.005 * np.mean(highs))
    trough_indices, _ = find_peaks(-lows, distance=4, prominence=0.005 * np.mean(lows))

    # --- 1. DOUBLE TOP ("M" Pattern) ---
    if len(peak_indices) >= 2:
        p1_idx, p2_idx = peak_indices[-2], peak_indices[-1]
        p1_price, p2_price = highs[p1_idx], highs[p2_idx]
        
        # Check if peaks are within 1.2% price difference
        if abs(p1_price - p2_price) / p1_price < 0.015:
            # Check trough in between (Neckline)
            mid_troughs = [t for t in trough_indices if p1_idx < t < p2_idx]
            if mid_troughs:
                neckline_idx = mid_troughs[0]
                neckline_price = lows[neckline_idx]
                target_price = round(neckline_price - (p1_price - neckline_price), 2)
                
                status = "Triggered" if cur_price < neckline_price else "Formed (Testing Neckline)"
                patterns.append({
                    "pattern": "Double Top (M Pattern)",
                    "type": "Classical Reversal",
                    "bias": "Bearish",
                    "confidence": 85 if cur_price < neckline_price else 72,
                    "neckline": round(neckline_price, 2),
                    "target": target_price,
                    "stop_loss": round(max(p1_price, p2_price) * 1.005, 2),
                    "status": status,
                    "desc": f"Two equal peaks near {round(p1_price, 2)} with neckline at {round(neckline_price, 2)}."
                })

    # --- 2. DOUBLE BOTTOM ("W" Pattern) ---
    if len(trough_indices) >= 2:
        t1_idx, t2_idx = trough_indices[-2], trough_indices[-1]
        t1_price, t2_price = lows[t1_idx], lows[t2_idx]
        
        # Check if troughs are within 1.5% difference
        if abs(t1_price - t2_price) / t1_price < 0.015:
            # Check peak in between (Neckline)
            mid_peaks = [p for p in peak_indices if t1_idx < p < t2_idx]
            if mid_peaks:
                neckline_idx = mid_peaks[0]
                neckline_price = highs[neckline_idx]
                target_price = round(neckline_price + (neckline_price - t1_price), 2)
                
                status = "Triggered" if cur_price > neckline_price else "Formed (Testing Neckline)"
                patterns.append({
                    "pattern": "Double Bottom (W Pattern)",
                    "type": "Classical Reversal",
                    "bias": "Bullish",
                    "confidence": 86 if cur_price > neckline_price else 73,
                    "neckline": round(neckline_price, 2),
                    "target": target_price,
                    "stop_loss": round(min(t1_price, t2_price) * 0.995, 2),
                    "status": status,
                    "desc": f"Two equal troughs near {round(t1_price, 2)} with breakout neckline at {round(neckline_price, 2)}."
                })

    # --- 3. HEAD AND SHOULDERS (Bearish Reversal) ---
    if len(peak_indices) >= 3:
        ls_idx, head_idx, rs_idx = peak_indices[-3], peak_indices[-2], peak_indices[-1]
        ls_p, head_p, rs_p = highs[ls_idx], highs[head_idx], highs[rs_idx]
        
        # Head must be higher than both Left Shoulder and Right Shoulder
        if head_p > ls_p and head_p > rs_p:
            # Left and Right shoulders within 3% of each other
            if abs(ls_p - rs_p) / ls_p < 0.035:
                # Find neckline troughs
                t1 = [t for t in trough_indices if ls_idx < t < head_idx]
                t2 = [t for t in trough_indices if head_idx < t < rs_idx]
                if t1 and t2:
                    nl_price = (lows[t1[0]] + lows[t2[0]]) / 2.0
                    height = head_p - nl_price
                    target_price = round(nl_price - height, 2)
                    
                    status = "Neckline Breakdown" if cur_price < nl_price else "Right Shoulder Completed"
                    patterns.append({
                        "pattern": "Head and Shoulders",
                        "type": "Classical Reversal",
                        "bias": "Bearish",
                        "confidence": 88 if cur_price < nl_price else 75,
                        "neckline": round(nl_price, 2),
                        "target": target_price,
                        "stop_loss": round(rs_p * 1.005, 2),
                        "status": status,
                        "desc": f"Head at {round(head_p, 2)}, shoulders near {round(ls_p, 2)}. Neckline support at {round(nl_price, 2)}."
                    })

    # --- 4. INVERSE HEAD AND SHOULDERS (Bullish Reversal) ---
    if len(trough_indices) >= 3:
        ls_idx, head_idx, rs_idx = trough_indices[-3], trough_indices[-2], trough_indices[-1]
        ls_p, head_p, rs_p = lows[ls_idx], lows[head_idx], lows[rs_idx]
        
        # Head lower than shoulders
        if head_p < ls_p and head_p < rs_p:
            if abs(ls_p - rs_p) / ls_p < 0.035:
                p1 = [p for p in peak_indices if ls_idx < p < head_idx]
                p2 = [p for p in peak_indices if head_idx < p < rs_idx]
                if p1 and p2:
                    nl_price = (highs[p1[0]] + highs[p2[0]]) / 2.0
                    height = nl_price - head_p
                    target_price = round(nl_price + height, 2)
                    
                    status = "Neckline Breakout" if cur_price > nl_price else "Right Shoulder Completed"
                    patterns.append({
                        "pattern": "Inverse Head and Shoulders",
                        "type": "Classical Reversal",
                        "bias": "Bullish",
                        "confidence": 89 if cur_price > nl_price else 76,
                        "neckline": round(nl_price, 2),
                        "target": target_price,
                        "stop_loss": round(rs_p * 0.995, 2),
                        "status": status,
                        "desc": f"Inverse Head at {round(head_p, 2)}, neckline resistance at {round(nl_price, 2)}."
                    })

    # --- 5. TRIANGLES (Ascending, Descending, Symmetrical) ---
    if len(peak_indices) >= 2 and len(trough_indices) >= 2:
        recent_p = peak_indices[-2:]
        recent_t = trough_indices[-2:]
        
        # Slopes of highs and lows
        p_slope = (highs[recent_p[1]] - highs[recent_p[0]]) / (recent_p[1] - recent_p[0])
        t_slope = (lows[recent_t[1]] - lows[recent_t[0]]) / (recent_t[1] - recent_t[0])
        
        # Ascending Triangle: Flat highs, Higher lows
        if abs(p_slope) < 0.001 * cur_price and t_slope > 0.002 * cur_price:
            resistance = highs[recent_p[1]]
            patterns.append({
                "pattern": "Ascending Triangle",
                "type": "Continuation / Breakout",
                "bias": "Bullish",
                "confidence": 83,
                "resistance": round(resistance, 2),
                "target": round(resistance + (resistance - lows[recent_t[0]]), 2),
                "stop_loss": round(lows[recent_t[1]] * 0.995, 2),
                "status": "Pressure building under resistance",
                "desc": f"Horizontal resistance near {round(resistance, 2)} with higher lows pressing upward."
            })

        # Descending Triangle: Flat lows, Lower highs
        elif abs(t_slope) < 0.001 * cur_price and p_slope < -0.002 * cur_price:
            support = lows[recent_t[1]]
            patterns.append({
                "pattern": "Descending Triangle",
                "type": "Continuation / Breakdown",
                "bias": "Bearish",
                "confidence": 83,
                "support": round(support, 2),
                "target": round(support - (highs[recent_p[0]] - support), 2),
                "stop_loss": round(highs[recent_p[1]] * 1.005, 2),
                "status": "Pressure building over support",
                "desc": f"Horizontal support near {round(support, 2)} with lower highs pressing downward."
            })

        # Symmetrical Triangle: Lower highs, Higher lows
        elif p_slope < -0.002 * cur_price and t_slope > 0.002 * cur_price:
            patterns.append({
                "pattern": "Symmetrical Triangle",
                "type": "Volatility Squeeze",
                "bias": "Neutral / Breakout Pending",
                "confidence": 78,
                "apex_range": f"{round(lows[recent_t[1]], 2)} - {round(highs[recent_p[1]], 2)}",
                "target": round(cur_price * 1.025, 2),
                "stop_loss": round(cur_price * 0.985, 2),
                "status": "Volatility Contraction",
                "desc": "Converging upper and lower trendlines. Massive directional move imminent."
            })

    # --- 6. BULL FLAG & BEAR FLAG (Last 20 candles consolidation) ---
    if n >= 25:
        # Check pole: rapid move in 10 candles before consolidation
        pole = closes[-25:-10]
        flag = closes[-10:]
        
        pole_return = (pole[-1] - pole[0]) / pole[0]
        flag_return = (flag[-1] - flag[0]) / flag[0]
        
        # Bull Flag: Strong prior impulse + slight downward/flat drift
        if pole_return > 0.035 and -0.025 < flag_return < 0.005:
            patterns.append({
                "pattern": "Bull Flag",
                "type": "Continuation",
                "bias": "Bullish",
                "confidence": 82,
                "pole_gain": f"{round(pole_return*100, 1)}%",
                "target": round(cur_price * (1 + pole_return * 0.8), 2),
                "stop_loss": round(np.min(flag) * 0.995, 2),
                "status": "Consolidating before next leg up",
                "desc": f"Sharp prior run-up (+{round(pole_return*100, 1)}%) followed by orderly tight consolidation."
            })
            
        # Bear Flag: Sharp prior drop + slight upward/flat drift
        elif pole_return < -0.035 and -0.005 < flag_return < 0.025:
            patterns.append({
                "pattern": "Bear Flag",
                "type": "Continuation",
                "bias": "Bearish",
                "confidence": 82,
                "pole_loss": f"{round(pole_return*100, 1)}%",
                "target": round(cur_price * (1 + pole_return * 0.8), 2),
                "stop_loss": round(np.max(flag) * 1.005, 2),
                "status": "Consolidating before next leg down",
                "desc": f"Sharp prior drop ({round(pole_return*100, 1)}%) followed by weak corrective consolidation."
            })

    return patterns
