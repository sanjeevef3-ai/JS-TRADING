"""
NIFTY Top Heavyweight Stocks Simultaneous Tracking & Institutional Trap Detection
Tracks HDFC Bank, Reliance, ICICI Bank, Infosys, TCS, ITC, L&T, SBI, etc.
Calculates Weighted Push Index and warns against Bull/Bear Traps.
"""

from typing import Dict, Any, List
import yfinance as yf
import pandas as pd
import numpy as np

# Top NIFTY 50 Heavyweights and their approximate index weights
HEAVYWEIGHT_WEIGHTS = {
    "HDFCBANK.NS": {"name": "HDFC Bank", "weight": 0.125},
    "RELIANCE.NS": {"name": "Reliance Ind", "weight": 0.098},
    "ICICIBANK.NS": {"name": "ICICI Bank", "weight": 0.082},
    "INFY.NS": {"name": "Infosys", "weight": 0.065},
    "ITC.NS": {"name": "ITC", "weight": 0.045},
    "TCS.NS": {"name": "TCS", "weight": 0.042},
    "LT.NS": {"name": "Larsen & Toubro", "weight": 0.040},
    "BHARTIARTL.NS": {"name": "Bharti Airtel", "weight": 0.038},
    "SBIN.NS": {"name": "State Bank of India", "weight": 0.035},
    "AXISBANK.NS": {"name": "Axis Bank", "weight": 0.032}
}

class HeavyweightTracker:
    """Tracks top index constituents to confirm institutional trend legitimacy."""

    def __init__(self):
        pass

    def get_heavyweights_snapshot(self) -> Dict[str, Any]:
        """
        Fetches live snapshots for all top 10 heavyweights simultaneously.
        """
        tickers = list(HEAVYWEIGHT_WEIGHTS.keys())
        data_table = []
        weighted_return_sum = 0.0
        total_weight = 0.0

        green_count = 0
        red_count = 0

        for ticker, meta in HEAVYWEIGHT_WEIGHTS.items():
            try:
                stk = yf.Ticker(ticker)
                fast = stk.fast_info
                last_p = getattr(fast, "last_price", None)
                prev_p = getattr(fast, "previous_close", None)
                
                if not last_p or np.isnan(last_p):
                    h = stk.history(period="2d", interval="1d")
                    last_p = float(h["Close"].iloc[-1]) if not h.empty else 1000.0
                    prev_p = float(h["Close"].iloc[-2]) if len(h) > 1 else last_p

                p_chg = round(((last_p - prev_p) / prev_p) * 100, 2) if prev_p else 0.0
                w = meta["weight"]

                weighted_return_sum += p_chg * w
                total_weight += w

                if p_chg > 0:
                    green_count += 1
                elif p_chg < 0:
                    red_count += 1

                data_table.append({
                    "ticker": ticker,
                    "name": meta["name"],
                    "weight_pct": round(w * 100, 1),
                    "price": round(float(last_p), 2),
                    "p_change": p_chg,
                    "bias": "BULLISH" if p_chg > 0 else ("BEARISH" if p_chg < 0 else "FLAT")
                })
            except Exception as e:
                pass

        # Institutional Net Push Index (-100 to +100 normalized)
        avg_weighted_move = (weighted_return_sum / total_weight) if total_weight > 0 else 0.0
        push_score = round(max(-100, min(100, avg_weighted_move * 45)), 1)

        # Check Top 2 Drivers (HDFC Bank & Reliance)
        hdfc_move = next((x["p_change"] for x in data_table if "HDFCBANK" in x["ticker"]), 0.0)
        rel_move = next((x["p_change"] for x in data_table if "RELIANCE" in x["ticker"]), 0.0)

        # Determine Trap Alert
        if push_score > 25 and (hdfc_move < -0.2 and rel_move < -0.2):
            trap_status = "⚠️ CAUTION: High Risk Bull Trap (Top Heavyweights Are Selling)"
        elif push_score < -25 and (hdfc_move > 0.2 and rel_move > 0.2):
            trap_status = "⚠️ CAUTION: High Risk Bear Trap (Top Heavyweights Are Accumulating)"
        elif push_score > 25:
            trap_status = "✅ TRUE INSTITUTIONAL BULL RUN (Heavyweights Strongly Supporting)"
        elif push_score < -25:
            trap_status = "🔻 TRUE INSTITUTIONAL SELLING (Heavyweights Dumping)"
        else:
            trap_status = "⚖️ Neutral / Mixed Heavyweight Consolidation"

        return {
            "heavyweight_push_score": push_score,
            "trap_status": trap_status,
            "green_constituents": green_count,
            "red_constituents": red_count,
            "top_drivers": {
                "hdfc_bank_change": hdfc_move,
                "reliance_change": rel_move
            },
            "constituents": data_table
        }
