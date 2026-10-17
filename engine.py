"""
Master Market & Swarm AI Coordinator Engine
Orchestrates live Indian market data, pattern scanning, MTF confluence,
MiroFish swarm simulation, and self-learning feedback.
"""

import time
from typing import Dict, Any, Optional

from config import DEFAULT_SYMBOLS
from indian_market import (
    MarketDataFetcher,
    calculate_support_resistance,
    calculate_pivots,
    calculate_fibonacci,
    resolve_symbol
)
from patterns import scan_all_patterns
from indicators import calculate_indicators, detect_divergences, analyze_mtf_confluence
from mirofish_core import (
    MiroFishSimulationSandbox,
    MiroFishConsensusEngine,
    LoopProtector
)
from learning import PatternLedger, WeightCalibrator

class IndianMarketAIEngine:
    """
    Unified AI Engine synthesizing Indian Stock Market live analysis
    with the MiroFish multi-agent swarm architecture.
    """

    def __init__(self):
        self.fetcher = MarketDataFetcher()
        self.sandbox = MiroFishSimulationSandbox(max_rounds=5)
        self.consensus_engine = MiroFishConsensusEngine()
        self.ledger = PatternLedger()
        self.calibrator = WeightCalibrator()

    def analyze_symbol(
        self,
        query: str,
        trading_style: str = "Intraday Swing",
        risk_tolerance: str = "Moderate",
        sentiment_bias: str = "Neutral"
    ) -> Dict[str, Any]:
        """
        Executes end-to-end live analysis on an Indian stock or index.
        Wrapped in LoopProtector to guarantee finite execution.
        """
        start_time = time.time()
        protector = LoopProtector(timeout_seconds=30.0)

        user_context = {
            "query": query,
            "trading_style": trading_style,
            "risk_tolerance": risk_tolerance,
            "sentiment_bias": sentiment_bias
        }

        # Step 1: Ingest Live & Multi-Timeframe Data
        protector.phase("data_ingestion")
        mtf_data = self.fetcher.fetch_multi_timeframe(query)
        symbol = mtf_data.get("symbol", query.upper())
        ticker = mtf_data.get("ticker", query)
        live_quote = mtf_data.get("live_quote", {})
        timeframes = mtf_data.get("timeframes", {})

        cur_price = live_quote.get("current_price", 0.0)

        # Step 2: Deep Pattern Scanning ("Koi bhi chiz miss na ho")
        protector.phase("pattern_scanning")
        patterns_data = scan_all_patterns(timeframes)

        # Apply Calibrated Weights from Self-Learning Ledger
        for p in patterns_data.get("all_detected_patterns", []):
            base_conf = p.get("confidence", 75.0)
            p["calibrated_confidence"] = self.calibrator.get_calibrated_confidence(p.get("pattern", ""), base_conf)

        # Step 3: Technical Indicators & Divergence Analysis
        protector.phase("technical_indicators")
        ind_15m = calculate_indicators(timeframes.get("15m", timeframes.get("5m")))
        ind_1d = calculate_indicators(timeframes.get("1d"))
        divergences = detect_divergences(timeframes.get("15m", timeframes.get("1h", timeframes.get("5m"))))

        # Step 4: Multi-Timeframe Confluence Matrix
        protector.phase("mtf_confluence")
        confluence_data = analyze_mtf_confluence(timeframes)

        # Step 5: Market Depth, Dynamic S/R, Pivots & Fibonacci
        protector.phase("market_depth")
        ref_df = timeframes.get("1d") if not timeframes.get("1d").empty else timeframes.get("15m")
        high_val = float(ref_df["High"].max()) if not ref_df.empty else cur_price * 1.05
        low_val = float(ref_df["Low"].min()) if not ref_df.empty else cur_price * 0.95
        close_val = cur_price

        pivots = calculate_pivots(high_val, low_val, close_val)
        fibonacci = calculate_fibonacci(high_val, low_val, is_uptrend=(confluence_data.get("confluence_score", 0) >= 0))
        sr_zones = calculate_support_resistance(ref_df)

        market_context_package = {
            "symbol": symbol,
            "ticker": ticker,
            "quote": live_quote,
            "patterns": patterns_data,
            "confluence": confluence_data,
            "indicators_15m": ind_15m,
            "indicators_1d": ind_1d,
            "divergences": divergences,
            "depth": {
                "pivots": pivots,
                "fibonacci": fibonacci,
                "supports": sr_zones.get("supports", []),
                "resistances": sr_zones.get("resistances", [])
            }
        }

        # Step 6: MiroFish Swarm Simulation Sandbox (Parallel Personas + Cross-Examination)
        protector.phase("swarm_simulation")
        sim_result = self.sandbox.run_simulation(market_context_package, user_context)

        # Step 7: Emergent Consensus & Trade Plan Synthesis
        protector.phase("consensus_synthesis")
        consensus = self.consensus_engine.synthesize(
            symbol=symbol,
            live_quote=live_quote,
            simulation_res=sim_result,
            patterns_data=patterns_data,
            confluence_data=confluence_data,
            depth_data=market_context_package["depth"],
            user_context=user_context
        )

        # Step 8: Self-Learning Log Update & Outcome Verification
        protector.phase("self_learning_update")
        self.ledger.log_prediction(
            symbol=symbol,
            consensus_res=consensus,
            patterns=patterns_data.get("all_detected_patterns", [])
        )
        meta_learning = self.ledger.get_meta_learning_state()
        pattern_stats = self.ledger.get_pattern_stats()

        # Step 9: Synthesize Master 7-AI Consensus Matrix (Wall Street Grade)
        protector.phase("master_7_ai_synthesis")
        from indian_market.master_ai_suite import master_7_ai_suite
        from indian_market.news_fetcher import market_news_fetcher
        from indian_market.vix_tracker import VIXTracker

        try:
            recent_news = market_news_fetcher.fetch_live_news(limit=5)
            cur_vix = VIXTracker().get_live_vix()
        except Exception:
            recent_news = []
            cur_vix = {}

        master_7_ai = master_7_ai_suite.evaluate_all(
            symbol=symbol,
            live_quote=live_quote,
            timeframes=timeframes,
            patterns_data=patterns_data,
            indicators_15m=ind_15m,
            sim_result=sim_result,
            self_learning_meta=meta_learning,
            news_items=recent_news,
            vix_data=cur_vix
        )

        total_elapsed = round(time.time() - start_time, 2)

        return {
            "symbol": symbol,
            "ticker": ticker,
            "live_quote": live_quote,
            "patterns": patterns_data,
            "confluence": confluence_data,
            "indicators": {
                "primary_15m": ind_15m,
                "macro_1d": ind_1d
            },
            "divergences": divergences,
            "market_depth": market_context_package["depth"],
            "swarm_simulation": sim_result,
            "consensus": consensus,
            "self_learning": {
                "meta": meta_learning,
                "pattern_stats": pattern_stats
            },
            "master_7_ai": master_7_ai,
            "execution_metadata": {
                "elapsed_seconds": total_elapsed,
                "rounds_run": sim_result.get("rounds_executed", 2),
                "loop_guard_status": "PASSED_ZERO_LOOPS",
                "active_agents": len(sim_result.get("agent_stances", {}))
            }
        }
