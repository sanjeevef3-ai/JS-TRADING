"""
Configuration for Indian Stock Market MiroFish AI Engine
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
REPORTS_DIR = BASE_DIR / "reports"

for directory in [DATA_DIR, KNOWLEDGE_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Default Indian Stock Market Symbols & Mapping
DEFAULT_SYMBOLS = {
    # Major Indices
    "NIFTY": "^NSEI",
    "NIFTY50": "^NSEI",
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "BANK NIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "SENSEX": "^BSESN",
    "MIDCPNIFTY": "NIFTY_MIDCAP_100.NS",
    # Top NSE Largecaps
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "INFY": "INFY.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "SBIN": "SBIN.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "AXISBANK": "AXISBANK.NS",
    "MARUTI": "MARUTI.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TITAN": "TITAN.NS",
    "ADANIENT": "ADANIENT.NS",
    "WIPRO": "WIPRO.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "INTELLECT": "INTELLECT.NS",
}

# Multi-Timeframe Defaults
SUPPORTED_TIMEFRAMES = ["5m", "15m", "1h", "1d"]
TIMEFRAME_PERIODS = {
    "5m": "5d",
    "15m": "1mo",
    "1h": "3mo",
    "1d": "1y",
    "1wk": "2y"
}

# MiroFish Swarm Simulation & Loop Guard Settings
# Hard limits to completely eliminate AI infinite loops (Dark Side of AI)
LOOP_GUARD = {
    "MAX_SWARM_ROUNDS": 2,          # Bounded debate passes
    "MAX_AGENT_RETRIES": 2,         # Circuit breaker for failures
    "WATCHDOG_TIMEOUT_SECONDS": 30, # Max total execution per query
    "ENABLE_CIRCUIT_BREAKER": True, # Automatically aborts if stuck
    "STRICT_DAG_EXECUTION": True    # Directed Acyclic Graph - NO cyclic loops
}

# Web Server Settings
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", 8000)))
DEBUG = False

