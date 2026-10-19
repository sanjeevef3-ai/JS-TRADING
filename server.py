"""
FastAPI Server for Indian Stock Market MiroFish AI Engine
Serves Web Dashboard and REST APIs for multi-timeframe market analysis.
"""

import os
import time
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config import SERVER_HOST, SERVER_PORT, DEFAULT_SYMBOLS
from engine import IndianMarketAIEngine
from learning import PatternLedger, SelfRefineEngine
from indian_market import resolve_symbol

app = FastAPI(
    title="Indian Stock Market MiroFish AI Engine",
    description="Multi-timeframe live analysis, chart patterns, and swarm intelligence prediction.",
    version="2.0.0"
)

from starlette.middleware.base import BaseHTTPMiddleware
from indian_market.trade_call_tracker import trade_call_tracker
from indian_market.autonomous_autopilot import autopilot_engine, order_flow_engine, global_macro_engine

APP_BUILD_VERSION = "20261019_v50"

class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        path = request.url.path
        if path == "/" or path.startswith("/static") or path.endswith(".html") or path == "/manifest.json" or path == "/sw.js":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = IndianMarketAIEngine()
ledger = PatternLedger()
refiner = SelfRefineEngine()

# Mount Static UI files
UI_DIR = Path(__file__).resolve().parent / "ui"
STATIC_DIR = UI_DIR / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/api/version")
def get_app_version():
    """Provides current server build version for zero-touch automatic hot-reloading."""
    return {
        "version": APP_BUILD_VERSION,
        "timestamp": int(time.time()),
        "status": "online"
    }

@app.api_route("/", methods=["GET", "HEAD"])
def serve_index():
    """Serves the main interactive dashboard."""
    index_file = UI_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Dashboard UI file not found")
    return FileResponse(index_file)

@app.get("/sw.js")
def serve_service_worker():
    """Serves the service worker with no-cache header."""
    sw_file = UI_DIR / "sw.js"
    if not sw_file.exists():
        raise HTTPException(status_code=404, detail="Service worker not found")
    return FileResponse(sw_file, media_type="application/javascript")

@app.get("/manifest.json")

def serve_manifest():
    manifest_file = UI_DIR / "manifest.json"
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail="Manifest not found")
    return FileResponse(manifest_file, media_type="application/manifest+json")

@app.get("/sw.js")
def serve_sw():
    sw_file = UI_DIR / "sw.js"
    if not sw_file.exists():
        raise HTTPException(status_code=404, detail="Service worker not found")
    return FileResponse(sw_file, media_type="application/javascript")

@app.get("/api/symbols")
def get_symbols():
    """Returns curated list of top Indian stocks and indices."""
    symbols = [
        {"name": "NIFTY 50", "symbol": "NIFTY", "ticker": "^NSEI", "type": "Index"},
        {"name": "BANK NIFTY", "symbol": "BANKNIFTY", "ticker": "^NSEBANK", "type": "Index"},
        {"name": "SENSEX", "symbol": "SENSEX", "ticker": "^BSESN", "type": "Index"},
        {"name": "Intellect Design Arena", "symbol": "INTELLECT", "ticker": "INTELLECT.NS", "type": "Stock"},
        {"name": "Reliance Industries", "symbol": "RELIANCE", "ticker": "RELIANCE.NS", "type": "Stock"},
        {"name": "Tata Consultancy Services", "symbol": "TCS", "ticker": "TCS.NS", "type": "Stock"},
        {"name": "HDFC Bank", "symbol": "HDFCBANK", "ticker": "HDFCBANK.NS", "type": "Stock"},
        {"name": "Infosys", "symbol": "INFY", "ticker": "INFY.NS", "type": "Stock"},
        {"name": "ICICI Bank", "symbol": "ICICIBANK", "ticker": "ICICIBANK.NS", "type": "Stock"},
        {"name": "Tata Motors", "symbol": "TATAMOTORS", "ticker": "TATAMOTORS.NS", "type": "Stock"},
        {"name": "State Bank of India", "symbol": "SBIN", "ticker": "SBIN.NS", "type": "Stock"},
        {"name": "Bharti Airtel", "symbol": "BHARTIARTL", "ticker": "BHARTIARTL.NS", "type": "Stock"},
        {"name": "Larsen & Toubro", "symbol": "LT", "ticker": "LT.NS", "type": "Stock"}
    ]
    return {"symbols": symbols}

@app.get("/api/analyze")
def analyze(
    symbol: str = Query(..., description="Stock or Index query, e.g. NIFTY, RELIANCE, TCS"),
    style: str = Query("Intraday Swing", description="Trading style: Intraday Scalp, Intraday Swing, Positional Delivery"),
    risk: str = Query("Moderate", description="Risk profile: Conservative, Moderate, Aggressive")
):
    """
    Main endpoint: runs full multi-timeframe analysis and MiroFish swarm simulation.
    """
    try:
        result = engine.analyze_symbol(
            query=symbol,
            trading_style=style,
            risk_tolerance=risk
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candles")
def get_candles(
    symbol: str = Query(..., description="Stock or Index query"),
    interval: str = Query("15m", description="Timeframe: 5m, 15m, 1h, 1d")
):
    """
    Returns OHLCV candles formatted for charting.
    """
    try:
        clean_name, ticker = resolve_symbol(symbol)
        df = engine.fetcher.fetch_timeframe_candles(ticker, interval)
        if df.empty:
            return {"symbol": clean_name, "interval": interval, "candles": []}
            
        candles = []
        for _, row in df.iterrows():
            candles.append({
                "time": str(row["time"]),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]) if row["Volume"] else 0
            })
            
        return {
            "symbol": clean_name,
            "ticker": ticker,
            "interval": interval,
            "candles": candles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from indian_market.options_engine import OptionsEngine

options_engine = OptionsEngine()

@app.get("/api/options/strategy")
def get_options_strategy(
    symbol: str = Query("NIFTY"),
    strategy: str = Query("Bull Call Spread", description="Bull Call Spread, Bear Put Spread, Iron Condor, Long Call")
):
    """Generates Opstra-style options strategy with Payoff, Greeks, Max Profit and Loss."""
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    strat = options_engine.build_opstra_strategy(clean_name, spot, strategy)
    return strat

@app.post("/api/options/demo-trade")
def execute_demo_trade(
    symbol: str = Query("NIFTY"),
    strategy: str = Query("Bull Call Spread")
):
    """Executes a live paper demo trade and adds it to the demo portfolio."""
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    strat = options_engine.build_opstra_strategy(clean_name, spot, strategy)
    trade = options_engine.execute_live_demo_trade(strat)
    return trade

@app.get("/api/options/demo-trades")
def get_open_demo_trades(symbol: str = Query("NIFTY")):
    """Returns list of open demo trades with real-time PnL tracking."""
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    trades = options_engine.get_demo_trades(live_spot=spot)
    return {"trades": trades}

@app.post("/api/options/kill-switch")
def emergency_kill_switch(symbol: str = Query("NIFTY")):
    """Emergency Kill-Switch (ScalpPro): Instantly closes all open positions and locks P&L."""
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    res = options_engine.close_all_demo_trades(live_spot=spot, reason="EMERGENCY KILL-SWITCH")
    return res

@app.post("/api/options/scalp-trade")
def execute_scalp_trade(symbol: str = Query("NIFTY"), action: str = Query("BUY_CE")):
    """ScalpPro 1-Tap Execution: Instantly enters ATM option with optimal limit and Zing targets."""
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    trade = options_engine.execute_scalp_order(clean_name, spot, action)
    return trade

@app.get("/api/options/chain")
def get_option_chain(symbol: str = Query("NIFTY")):
    """Returns simulated Option Chain with Black-Scholes Greeks."""
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    chain = options_engine.generate_option_chain(spot)
    return {"symbol": clean_name, "spot": spot, "chain": chain}

from indian_market.stock_catalog import search_portfolio_assets, get_option_builder_data, STOCK_CATALOG
import json

@app.get("/api/portfolio/catalog")
def get_portfolio_catalog():
    """Returns complete catalog of 110+ Indian stocks, indices & sectors for Order Pad and Portfolio."""
    return {"count": len(STOCK_CATALOG), "catalog": STOCK_CATALOG}

@app.get("/api/portfolio/search")
def search_portfolio(
    q: str = Query("", description="Search query for stocks, indices, or option contracts"),
    type: str = Query("ALL", description="Filter type: ALL, STOCK, OPTION")
):
    """Searches stock catalog, indices, and generates live option contracts (CE/PE)."""
    live_cache = {}
    try:
        for sym, tkr in [("NIFTY", "^NSEI"), ("BANKNIFTY", "^NSEBANK"), ("FINNIFTY", "NIFTY_FIN_SERVICE.NS"), ("RELIANCE", "RELIANCE.NS"), ("TCS", "TCS.NS"), ("HDFCBANK", "HDFCBANK.NS")]:
            q_data = engine.fetcher.get_live_quote(tkr)
            if q_data and q_data.get("current_price"):
                live_cache[sym] = {"price": q_data.get("current_price"), "p_change": q_data.get("change_pct", 0.0)}
    except Exception:
        pass
    results = search_portfolio_assets(query=q, filter_type=type, live_cache=live_cache)
    return {"query": q, "filter_type": type, "count": len(results), "results": results}

@app.get("/api/portfolio/option-builder")
def get_option_builder(symbol: str = Query("NIFTY", description="Underlying symbol e.g. NIFTY, BANKNIFTY, FINNIFTY, RELIANCE")):
    """Returns strike ladder and Black-Scholes CE/PE pricing for interactive Option Builder."""
    live_cache = {}
    clean_name, ticker = resolve_symbol(symbol)
    try:
        q_data = engine.fetcher.get_live_quote(ticker)
        if q_data and q_data.get("current_price"):
            live_cache[clean_name] = {"price": q_data.get("current_price"), "p_change": q_data.get("change_pct", 0.0)}
    except Exception:
        pass
    data = get_option_builder_data(underlying_sym=symbol, live_cache=live_cache)
    return data

from indian_market.live_oi_tracker import LiveOITracker
from indian_market.heavyweights import HeavyweightTracker
from indian_market.vix_tracker import VIXTracker
from indian_market.momentum_scanner import MomentumScanner
from indian_market.dhan_connector import DhanConnector
from indian_market.news_fetcher import market_news_fetcher

oi_tracker = LiveOITracker()
heavyweight_tracker = HeavyweightTracker()
vix_tracker = VIXTracker()
momentum_scanner = MomentumScanner()
dhan_connector = DhanConnector()

@app.get("/api/notifications/live")
def get_live_notifications():
    """
    Consolidated real-time notifications endpoint:
    Combines High-Conviction Trades, Pre-Breakout alerts, Breaking Financial News, and India VIX alerts.
    All items are timestamped with full Date & Time.
    Market Hours Enforced: Intraday CE/PE trade alerts are ONLY active during 09:15–15:30 IST.
    """
    session_info = momentum_scanner.check_market_session()
    cur_datetime_str = session_info["server_time_ist"]
    cur_time_clock = time.strftime("%H:%M:%S")

    # 1. Momentum & Pre-Breakout alerts (momentum_scanner handles market_session check internally)
    mom_data = momentum_scanner.scan_all_signals()
    trade_notifications = mom_data.get("notifications", [])

    # 2. Live Market News
    news_items = market_news_fetcher.fetch_live_news(limit=8)

    # 3. Live India VIX alert (only when market is live)
    vix_notifs = []
    if session_info["is_market_open"]:
        vix_data = vix_tracker.get_live_vix()
        vix_val = float(vix_data.get("vix_value", 14.5))
        vix_change = float(vix_data.get("change", 0.0))

        if abs(vix_change) >= 3.0 or vix_val >= 18.0:
            vix_notifs.append({
                "id": f"VIX_SPIKE_{round(vix_val, 1)}",
                "type": "VIX",
                "priority": "HIGH" if vix_val >= 18.0 else "NORMAL",
                "is_important": True,
                "title": f"📊 INDIA VIX ALERT: {vix_val} ({'+' if vix_change>=0 else ''}{vix_change:.2f}%)",
                "message": f"Market Volatility {'badh gayi hai (Spike)' if vix_change>0 else 'ghat gayi hai'}. Expected Daily Range: ±{vix_data.get('expected_daily_range_pts', 180)} pts. {vix_data.get('regime_action', '')}",
                "symbol": "INDIAVIX",
                "price": vix_val,
                "timestamp": cur_datetime_str,
                "time_clock": cur_time_clock
            })

    # 4. Evaluate Active Daily Calls for Target Hits (TG1/TG2) & Stop-Loss (SL) Hits
    live_prices = {}
    for item in (mom_data.get("fast_movers", []) + mom_data.get("diamond_trades", []) + mom_data.get("pre_breakout_alerts", [])):
        if "symbol" in item and "price" in item:
            try:
                live_prices[item["symbol"]] = float(item["price"])
            except Exception:
                pass
    
    # Also register any active fast_movers/diamond signals into daily ledger automatically
    for d in (mom_data.get("diamond_trades", []) + mom_data.get("fast_movers", [])):
        if "BUY" in str(d.get("action", "")).upper():
            try:
                trade_call_tracker.register_trade_call({
                    "symbol": d.get("symbol", ""),
                    "action": d.get("action", ""),
                    "call_type": "DIAMOND_90" if d.get("is_diamond") else "MOMENTUM_BUY",
                    "entry_price": d.get("optimal_limit_price") or d.get("price"),
                    "target_1": d.get("target_1"),
                    "target_2": d.get("target_2"),
                    "stop_loss": d.get("hard_sl"),
                    "win_probability_pct": d.get("win_probability_pct", 88.0)
                })
            except Exception:
                pass

    outcome_notifs = trade_call_tracker.evaluate_all_active_calls(live_prices)

    # 🤖 v50 Autonomous Auto-Pilot Live Evaluation
    ap_actions = []
    try:
        candidate_signals = mom_data.get("diamond_trades", []) + mom_data.get("fast_movers", [])
        ap_actions = autopilot_engine.evaluate_live_market(candidate_signals, live_prices)
    except Exception as e:
        print(f"[AutoPilot evaluation error]: {e}")

    ap_notifs = []
    for act in ap_actions:
        act_type = str(act.get("type", "")).upper()
        is_tg = "TG" in act_type or "TARGET" in act_type
        is_sl = "SL" in act_type
        outcome_kind = act.get("outcome_kind") or ("TG2" if "TARGET2" in act_type or "TG2" in act_type else ("TG1" if "TG1" in act_type else ("SL" if is_sl else None)))
        
        ap_notifs.append({
            "id": f"AP_NOTIF_{int(time.time()*1000)}_{act_type}",
            "type": "TARGET_HIT" if is_tg else ("SL_HIT" if is_sl else "TRADE"),
            "outcome_kind": outcome_kind,
            "priority": "DIAMOND_90_URGENT",
            "is_important": True,
            "is_outcome": bool(is_tg or is_sl),
            "symbol": act.get("symbol", "NIFTY"),
            "action": act.get("trade", {}).get("action", "BUY"),
            "price": act.get("trade", {}).get("entry_price"),
            "title": f"🤖 AUTOPILOT: {act.get('type')}",
            "message": act.get("message", ""),
            "voice_text": act.get("voice_text", act.get("message", "")),
            "timestamp": cur_datetime_str,
            "sound": "target_hit" if is_tg else ("sl_hit" if is_sl else "trade")
        })

    # Combine all: Outcome alerts (TG Hit / SL Hit / Auto-Pilot) ALWAYS take HIGHEST PRIORITY at top!
    all_notifs = []
    all_notifs.extend(ap_notifs)
    all_notifs.extend(outcome_notifs)
    all_notifs.extend(trade_notifications)
    all_notifs.extend(vix_notifs)
    all_notifs.extend(news_items)

    today_summary = trade_call_tracker.get_today_summary()
    today_calls = trade_call_tracker.get_all_calls()

    return {
        "status": "success",
        "market_session": session_info,
        "is_market_open": session_info["is_market_open"],
        "server_time": cur_datetime_str,
        "total_count": len(all_notifs),
        "notifications": all_notifs,
        "diamond_trades": mom_data.get("diamond_trades", []),
        "diamond_count": mom_data.get("diamond_count", 0),
        "today_outcomes_summary": today_summary,
        "today_calls": today_calls,
        "autopilot_status": autopilot_engine.get_status(),
        "global_regime": mom_data.get("global_regime", "BALANCED REGIME"),
        "global_advice": mom_data.get("global_advice", "")
    }

@app.get("/api/signals/daily-outcomes")
def get_daily_trade_outcomes():
    """Returns today's complete Buy/Sell calls ledger, win rate, and Target/SL hit outcomes."""
    return {
        "status": "success",
        "summary": trade_call_tracker.get_today_summary(),
        "calls": trade_call_tracker.get_all_calls()
    }

@app.post("/api/signals/simulate-outcome")
def simulate_trade_outcome(call_id: str = Query(""), outcome_type: str = Query("TG1")):
    """Simulates TG1, TG2, or SL hit for testing audio chimes and pop-flash notifications."""
    res = trade_call_tracker.simulate_outcome(call_id, outcome_type)
    return res

# ═══════════════════════════════════════════════════════════════════════
# 🤖 v50 AUTONOMOUS QUANT AUTO-PILOT & INSTITUTIONAL SUITE REST ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@app.get("/api/autopilot/status")
def get_autopilot_status():
    """Returns real-time status, active positions, trailing SL state, and audit logs of Auto-Pilot."""
    return {
        "status": "success",
        "autopilot": autopilot_engine.get_status()
    }

@app.post("/api/autopilot/toggle")
def toggle_autopilot_state(enable: bool = Query(True), mode: str = Query("AUTO_PAPER")):
    """Engages or disengages the Autonomous Auto-Pilot."""
    res = autopilot_engine.toggle(enable, mode)
    return {"status": "success", "autopilot": res}

@app.post("/api/autopilot/panic-kill")
def panic_kill_switch():
    """Emergency circuit breaker: squares off all auto positions instantly and locks Auto-Pilot."""
    return autopilot_engine.panic_kill_all()

@app.get("/api/orderflow/snapshot")
def get_order_flow_snapshot(symbol: str = Query("NIFTY")):
    """Returns Level-3 Bid x Ask Order Flow Delta, CVD, and Big Whale Iceberg clusters."""
    return {
        "status": "success",
        "order_flow": order_flow_engine.get_order_flow_snapshot(symbol)
    }

@app.get("/api/macro/matrix")
def get_global_macro_matrix():
    """Returns US Futures, DXY, Crude Oil, 10Y Yields, and Gift Nifty gap prediction."""
    return {
        "status": "success",
        "macro": global_macro_engine.get_macro_matrix()
    }

@app.get("/api/options/oi")
def get_live_oi_data(symbol: str = Query("NIFTY")):
    """Returns strike-wise Call OI vs Put OI, PCR, Max Pain, and S/R levels."""
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    data = oi_tracker.calculate_oi_metrics(spot)
    return data

@app.get("/api/market/heavyweights")
def get_heavyweights_data():
    """Returns real-time status of top 10 heavyweights and Bull/Bear trap alerts."""
    return heavyweight_tracker.get_heavyweights_snapshot()

@app.get("/api/market/vix")
def get_vix_data():
    """Returns continuous India VIX, daily expected move, and volatility regime."""
    return vix_tracker.get_live_vix()

@app.get("/api/market/momentum-fast")
def get_fast_momentum():
    """Returns Pre-Breakout alerts, Fast Momentum (Call/Put Buy), Option Selling candidates, and Live Notifications."""
    return momentum_scanner.scan_all_signals()

@app.get("/api/options/adaptive-regime")
def get_adaptive_option_regime(symbol: str = Query("NIFTY")):
    """
    Automatically determines whether to BUY CALL/PUT (Fast Momentum / Pre-Breakout)
    or SELL OPTIONS (Low Momentum / Sideways Theta Decay) for the selected symbol.
    """
    clean_name, ticker = resolve_symbol(symbol)
    quote = engine.fetcher.get_live_quote(ticker)
    spot = quote.get("current_price", 22500.0)
    vix_data = vix_tracker.get_live_vix()
    vix_val = float(vix_data.get("vix_value", 14.5))

    scan_data = momentum_scanner.scan_all_signals()
    all_scanned = (
        scan_data.get("fast_movers", []) +
        scan_data.get("pre_breakout_alerts", []) +
        scan_data.get("option_selling_candidates", [])
    )
    matched = next((x for x in all_scanned if x["symbol"].upper() in symbol.upper() or symbol.upper() in x["symbol"].upper()), None)

    if matched:
        mom_score = matched["momentum_score"]
        sqz_score = matched["squeeze_score"]
        dir_bias = matched["direction"]
    else:
        mom_score = scan_data.get("avg_market_momentum", 45.0)
        sqz_score = scan_data.get("avg_market_squeeze", 50.0)
        dir_bias = "BULLISH" if quote.get("change", 0) >= 0 else "BEARISH"

    return options_engine.recommend_adaptive_regime_strategy(
        symbol=clean_name,
        spot=spot,
        momentum_score=mom_score,
        squeeze_score=sqz_score,
        direction_bias=dir_bias,
        vix=vix_val
    )

@app.get("/api/dhan/status")
def get_dhan_status():
    """Returns Dhan API connection state and token generation instructions."""
    conn = dhan_connector.test_connection()
    instructions = dhan_connector.get_token_generation_instructions()
    return {"connection": conn, "instructions": instructions}

@app.post("/api/dhan/configure")
def configure_dhan(client_id: str = Query(...), access_token: str = Query(...)):
    """Saves Dhan API credentials and connects client."""
    ok = dhan_connector.save_credentials(client_id, access_token)
    return {"success": ok, "connection": dhan_connector.test_connection()}

@app.post("/api/historical/download")
def trigger_historical_download():
    """Triggers download of 10-year historical datasets into data/historical/."""
    from data.historical_downloader import download_historical_datasets
    res = download_historical_datasets()
    return res

import math

def _sanitize_json_floats(obj):
    """Recursively replaces NaN, Infinity, -Infinity with None or 0.0 to prevent JSON compliant serialization crashes."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return obj
    elif isinstance(obj, dict):
        return {k: _sanitize_json_floats(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_sanitize_json_floats(v) for v in obj]
    return obj

from indian_market.super_portal import SuperPortalEngine
super_portal_engine = SuperPortalEngine()

@app.get("/api/market/super-portal")
def get_super_portal(symbol: str = Query("NIFTY")):
    """Returns combined Moneycontrol, Rediff Moneywiz Company 360, Investing.com Technical Gauge & TradingView symbol."""
    data = super_portal_engine.get_super_portal_data(symbol)
    return _sanitize_json_floats(data)

@app.get("/api/live-tv/streams")
def get_live_tv_streams():
    """Returns live stream URLs for CNBC Awaaz, Zee Business, ET Now Swadesh, CNBC-TV18, and NDTV Profit."""
    return super_portal_engine.get_live_tv_streams()

@app.get("/api/learning/stats")
def get_learning_stats():
    """Returns self-learning ledger pattern win rates, meta-learning generation, and learned lessons."""
    stats = ledger.get_pattern_stats()
    meta = ledger.get_meta_learning_state()
    return {"stats": stats, "meta": meta}

@app.post("/api/learning/refine")
def trigger_self_refine(symbol: str = Query("NIFTY")):
    """Triggers autonomous self-learning walk-forward calibration and system health check."""
    report = refiner.run_full_self_refinement(symbol=symbol)
    return report

import json
from fastapi import Body

from fastapi import Header

ADMIN_CONFIG_PATH = Path(__file__).resolve().parent / "data" / "dashboard_config.json"
ADMIN_PIN_PATH = Path(__file__).resolve().parent / "data" / "admin_pin.json"
DEFAULT_OWNER_PIN = "9782"  # Default PIN: last 4 digits of Jyoti Singh's Client ID (1000659782)

def _get_saved_admin_pin() -> str:
    try:
        if ADMIN_PIN_PATH.exists():
            data = json.loads(ADMIN_PIN_PATH.read_text(encoding="utf-8"))
            pin = str(data.get("pin", "")).strip()
            if pin:
                return pin
    except Exception:
        pass
    return DEFAULT_OWNER_PIN

def _verify_pin(pin_to_check: Optional[str]) -> bool:
    if not pin_to_check:
        return False
    return str(pin_to_check).strip() == _get_saved_admin_pin()

@app.post("/api/admin/verify-pin")
def verify_admin_pin(payload: dict = Body(...)):
    """Verifies if the entered Owner PIN is valid before unlocking Back Panel / Visual Edit Mode."""
    entered = str(payload.get("pin", "")).strip()
    if _verify_pin(entered):
        return {"valid": True, "message": "Unlocked! Welcome Jyoti Singh."}
    raise HTTPException(status_code=403, detail="Invalid Owner PIN! Only Jyoti Singh can unlock Back Panel.")

@app.post("/api/admin/change-pin")
def change_admin_pin(payload: dict = Body(...)):
    """Allows the owner to change her secret Admin PIN."""
    current_pin = str(payload.get("current_pin", "")).strip()
    new_pin = str(payload.get("new_pin", "")).strip()
    if not _verify_pin(current_pin):
        raise HTTPException(status_code=403, detail="Current PIN is incorrect.")
    if len(new_pin) < 4:
        raise HTTPException(status_code=400, detail="New PIN must be at least 4 characters.")
    ADMIN_PIN_PATH.parent.mkdir(parents=True, exist_ok=True)
    ADMIN_PIN_PATH.write_text(json.dumps({"pin": new_pin}, indent=2), encoding="utf-8")
    return {"success": True, "message": "Owner PIN updated successfully!"}

@app.get("/api/admin/config")
def get_admin_dashboard_config():
    """Returns saved dynamic back-panel configuration for Jyoti Singh's terminal (without exposing PIN)."""
    try:
        if ADMIN_CONFIG_PATH.exists():
            data = json.loads(ADMIN_CONFIG_PATH.read_text(encoding="utf-8"))
            data.pop("adminPin", None)
            return data
    except Exception:
        pass
    return {"configured": False}

@app.post("/api/admin/config")
def save_admin_dashboard_config(payload: dict = Body(...), x_admin_pin: Optional[str] = Header(default=None)):
    """Saves dynamic back-panel configuration — protected by Owner PIN!"""
    pin_candidate = x_admin_pin or payload.get("adminPin")
    if not _verify_pin(pin_candidate):
        raise HTTPException(status_code=403, detail="Unauthorized: Valid Owner PIN required to save dashboard changes.")
    try:
        ADMIN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        clean_payload = dict(payload)
        clean_payload.pop("adminPin", None)
        clean_payload["configured"] = True
        ADMIN_CONFIG_PATH.write_text(json.dumps(clean_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"success": True, "config": clean_payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/admin/config")
def reset_admin_dashboard_config(x_admin_pin: Optional[str] = Header(default=None)):
    """Resets dynamic back-panel configuration to default — protected by Owner PIN!"""
    if not _verify_pin(x_admin_pin):
        raise HTTPException(status_code=403, detail="Unauthorized: Valid Owner PIN required to reset dashboard.")
    try:
        if ADMIN_CONFIG_PATH.exists():
            ADMIN_CONFIG_PATH.unlink()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import socket

TUNNEL_URL_FILE = Path(__file__).resolve().parent / "data" / "mobile_tunnel_url.txt"

@app.get("/api/mobile-access")
def get_mobile_access_info():
    """Returns local Wi-Fi LAN URL and public HTTPS mobile tunnel URL."""
    lan_ip = "192.168.1.4"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    lan_url = f"http://{lan_ip}:{SERVER_PORT}"
    public_url = ""
    try:
        if TUNNEL_URL_FILE.exists():
            public_url = TUNNEL_URL_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return {
        "lan_ip": lan_ip,
        "lan_url": lan_url,
        "public_url": public_url,
        "primary_mobile_url": public_url if public_url else lan_url
    }

if __name__ == "__main__":
    print(f"Starting Personal AI Super Trading Terminal Server on http://{SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run("server:app", host=SERVER_HOST, port=SERVER_PORT, reload=False)




