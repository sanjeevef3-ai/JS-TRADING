"""
MiroFish Emergent Consensus Engine & Trade Plan Generator
Synthesizes swarm debate into a high-conviction, mathematically grounded trade plan.
"""

from typing import Dict, Any, List
import numpy as np

class MiroFishConsensusEngine:
    """
    Synthesizes emergent swarm consensus into probabilistic trading predictions
    with exact Entry, Stop Loss, Target 1, Target 2, Target 3, and Risk-Reward.
    """

    def synthesize(
        self,
        symbol: str,
        live_quote: Dict[str, Any],
        simulation_res: Dict[str, Any],
        patterns_data: Dict[str, Any],
        confluence_data: Dict[str, Any],
        depth_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Consensus synthesis logic.
        """
        cur_price = live_quote.get("current_price", 1000.0)
        stances = simulation_res.get("agent_stances", {})
        
        # 1. Compute 100-Agent Centurion Swarm Probability Distribution
        if "buy_votes" in simulation_res and "sell_votes" in simulation_res:
            b_votes = float(simulation_res.get("buy_votes", 0))
            s_votes = float(simulation_res.get("sell_votes", 0))
            h_votes = float(simulation_res.get("hold_votes", 0))
            tot = max(1.0, b_votes + s_votes + h_votes)
            bull_pct = round((b_votes / tot) * 100.0, 1)
            bear_pct = round((s_votes / tot) * 100.0, 1)
            neutral_pct = round((h_votes / tot) * 100.0, 1)
        else:
            bull_votes = 0.0
            bear_votes = 0.0
            neutral_votes = 0.0
            total_weight = 0.0
            for agent_name, st in stances.items():
                conf = 70.0
                verdict = "Neutral"
                if isinstance(st, dict):
                    conf = st.get("confidence", 70.0)
                    verdict = st.get("verdict", "Neutral")
                elif isinstance(st, str):
                    verdict = st
                total_weight += conf
                if "BUY" in str(verdict).upper() or "BULL" in str(verdict).upper():
                    bull_votes += conf
                elif "SELL" in str(verdict).upper() or "BEAR" in str(verdict).upper():
                    bear_votes += conf
                else:
                    neutral_votes += conf
            if total_weight > 0:
                bull_pct = round((bull_votes / total_weight) * 100, 1)
                bear_pct = round((bear_votes / total_weight) * 100, 1)
                neutral_pct = round((neutral_votes / total_weight) * 100, 1)
            else:
                bull_pct, bear_pct, neutral_pct = 50.0, 50.0, 0.0

        # 2. Determine Primary Direction
        if bull_pct >= 62:
            direction = "STRONG BULLISH"
            bias_action = "BUY / LONG"
        elif bull_pct >= 50:
            direction = "MODERATE BULLISH"
            bias_action = "BUY ON DIPS"
        elif bear_pct >= 62:
            direction = "STRONG BEARISH"
            bias_action = "SELL / SHORT"
        elif bear_pct >= 50:
            direction = "MODERATE BEARISH"
            bias_action = "SELL ON RISES"
        else:
            direction = "NEUTRAL / CHOPPY"
            bias_action = "NO TRADE / WAIT FOR BREAKOUT"

        # 3. Dynamic Trade Plan Calibration
        risk_stance = stances.get("Kavita (Risk Sentinel & Circuit Breaker)", {})
        stop_dist = risk_stance.get("recommended_stop_distance", cur_price * 0.01)
        t1_dist = risk_stance.get("recommended_target1_distance", stop_dist * 1.5)
        t2_dist = risk_stance.get("recommended_target2_distance", stop_dist * 2.5)

        supports = depth_data.get("supports", [])
        resistances = depth_data.get("resistances", [])

        # Fine-tune stop loss & targets using nearest S/R if available
        if "BULLISH" in direction:
            # Entry: Near current price or minor pullback
            entry_min = round(cur_price - (stop_dist * 0.25), 2)
            entry_max = round(cur_price + (stop_dist * 0.15), 2)
            entry_str = f"₹{entry_min} - ₹{entry_max}"
            
            # Stop loss below nearest support or ATR
            if supports and supports[0] < cur_price and (cur_price - supports[0]) < stop_dist * 1.6:
                stop_loss = round(supports[0] * 0.997, 2)
            else:
                stop_loss = round(cur_price - stop_dist, 2)

            target_1 = round(cur_price + t1_dist, 2)
            target_2 = round(cur_price + t2_dist, 2)
            target_3 = round(cur_price + (t2_dist * 1.4), 2)
            invalidation = f"15-minute close below ₹{stop_loss} or breakdown of recent swing low."

        elif "BEARISH" in direction:
            entry_min = round(cur_price - (stop_dist * 0.15), 2)
            entry_max = round(cur_price + (stop_dist * 0.25), 2)
            entry_str = f"₹{entry_min} - ₹{entry_max}"
            
            # Stop loss above nearest resistance or ATR
            if resistances and resistances[0] > cur_price and (resistances[0] - cur_price) < stop_dist * 1.6:
                stop_loss = round(resistances[0] * 1.003, 2)
            else:
                stop_loss = round(cur_price + stop_dist, 2)

            target_1 = round(cur_price - t1_dist, 2)
            target_2 = round(cur_price - t2_dist, 2)
            target_3 = round(cur_price - (t2_dist * 1.4), 2)
            invalidation = f"15-minute close above ₹{stop_loss} or breakout of recent swing high."
        else:
            entry_str = f"Wait for Breakout above ₹{round(cur_price + stop_dist, 2)} or below ₹{round(cur_price - stop_dist, 2)}"
            stop_loss = round(cur_price - (stop_dist * 0.7), 2)
            target_1 = round(cur_price + stop_dist, 2)
            target_2 = round(cur_price + (stop_dist * 1.8), 2)
            target_3 = round(cur_price + (stop_dist * 2.5), 2)
            invalidation = "Market trapped in sideways range. Avoid high leverage."

        # Risk-to-Reward calculation
        effective_risk = abs(cur_price - stop_loss)
        effective_reward = abs(target_1 - cur_price)
        rr_ratio = round(effective_reward / effective_risk, 2) if effective_risk > 0 else 1.5

        # Market Regime
        conf_state = confluence_data.get("confluence_state", "Normal")
        pattern_bias = patterns_data.get("pattern_bias", "Consolidating")
        
        regime = f"{pattern_bias} in {conf_state}"

        # MiroFish Executive Synthesis Summary
        executive_summary = (
            f"100 AI Agent Centurion Swarm debated {symbol} across 10 specialized divisions. "
            f"Collective consensus reached a {direction} posture ({bull_pct}% Bulls vs {bear_pct}% Bears). "
            f"Primary trade recommendation is '{bias_action}'. "
            f"Recommended Entry Zone is {entry_str} with Invalidation Stop-Loss at Rs.{stop_loss} "
            f"targeting T1: Rs.{target_1}, T2: Rs.{target_2}, and T3: Rs.{target_3} (R:R ratio 1:{rr_ratio})."
        )

        return {
            "symbol": symbol,
            "current_price": cur_price,
            "direction": direction,
            "recommended_action": bias_action,
            "probability_matrix": {
                "bullish_pct": bull_pct,
                "bearish_pct": bear_pct,
                "sideways_pct": neutral_pct
            },
            "trade_plan": {
                "entry_zone": entry_str,
                "stop_loss": stop_loss,
                "target_1": target_1,
                "target_2": target_2,
                "target_3": target_3,
                "risk_reward_ratio": f"1 : {rr_ratio}",
                "invalidation_criteria": invalidation
            },
            "market_regime": regime,
            "executive_summary": executive_summary,
            "timestamp": live_quote.get("timestamp")
        }
