"""
India VIX (Volatility Index) Continuous Tracker & Strategy Calibrator
Computes real-time volatility regime, expected daily range, and optimal strategy recommendations.
"""

import math
from typing import Dict, Any
import yfinance as yf

class VIXTracker:
    """Tracks ^INDIAVIX live and translates volatility into risk limits."""

    def __init__(self):
        pass

    def get_live_vix(self) -> Dict[str, Any]:
        """
        Fetches live India VIX and calculates volatility implications.
        """
        try:
            vix_ticker = yf.Ticker("^INDIAVIX")
            hist = vix_ticker.history(period="5d", interval="15m")
            
            if hist.empty:
                vix_val = 14.5
                prev_vix = 14.5
            else:
                vix_val = float(hist["Close"].iloc[-1])
                prev_vix = float(hist["Close"].iloc[-2]) if len(hist) > 1 else vix_val

            vix_change = round(vix_val - prev_vix, 2)
            vix_p_change = round((vix_change / prev_vix) * 100, 2) if prev_vix else 0.0

            # Daily Expected Move Formula: VIX / sqrt(252)
            expected_daily_move_pct = round(vix_val / math.sqrt(252), 2)

            # Volatility Classification
            if vix_val < 12.0:
                regime = "Low Volatility (Chop / Sideways Dominance)"
                strat_rec = "Non-Directional Spreads (Iron Condor / Short Strangles)"
                risk_level = "LOW (Premiums Cheap, Low Decay Speed)"
            elif 12.0 <= vix_val <= 16.5:
                regime = "Optimal Volatility (Smooth Directional Trends)"
                strat_rec = "Directional Vertical Spreads (Bull Call / Bear Put Spread)"
                risk_level = "BALANCED (Ideal for Trend Following)"
            elif 16.5 < vix_val <= 21.0:
                regime = "Elevated Volatility (High Gamma Swings)"
                strat_rec = "Wide Hedged Spreads + Strict Trailing Stops"
                risk_level = "ELEVATED (Avoid Tight Stop-Losses)"
            else:
                regime = "Extreme Panic / Event Volatility (Wild Market Moves)"
                strat_rec = "Long Options Straddles or Capital Preservation"
                risk_level = "HIGH RISK (Cut Lot Sizes by 50%)"

            return {
                "vix_value": round(vix_val, 2),
                "vix_change": vix_change,
                "vix_p_change": vix_p_change,
                "expected_daily_move_pct": f"±{expected_daily_move_pct}%",
                "volatility_regime": regime,
                "strategy_recommendation": strat_rec,
                "risk_environment": risk_level
            }
        except Exception as e:
            return {
                "vix_value": 14.5,
                "error": str(e),
                "volatility_regime": "Optimal Volatility"
            }
