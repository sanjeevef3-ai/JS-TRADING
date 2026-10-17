"""
Indian Stock Market Symbol Resolver
Maps natural user inputs (e.g., 'nifty', 'reliance', 'banknifty', 'tcs')
to valid exchange tickers (e.g., '^NSEI', 'RELIANCE.NS', '^NSEBANK').
"""

import re
from typing import Tuple
from config import DEFAULT_SYMBOLS

ALIASES = {
    "NIFTY": "^NSEI",
    "NIFTY50": "^NSEI",
    "NIFTY 50": "^NSEI",
    "NIFTY-50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "BANK NIFTY": "^NSEBANK",
    "BANK-NIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "SENSEX": "^BSESN",
    "BSE SENSEX": "^BSESN",
    "MIDCAPNIFTY": "NIFTY_MIDCAP_100.NS",
    "NIFTYIT": "^CNXIT",
    "NIFTY IT": "^CNXIT",
    "HDFC": "HDFCBANK.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "TATA STEEL": "TATASTEEL.NS",
    "STATE BANK": "SBIN.NS",
    "SBI": "SBIN.NS",
    "BHARTI AIRTEL": "BHARTIARTL.NS",
    "AIRTEL": "BHARTIARTL.NS",
    "L&T": "LT.NS",
    "LARSEN": "LT.NS",
    "BAJAJ FINANCE": "BAJFINANCE.NS",
    "BAJAJ FINSERV": "BAJAJFINSV.NS",
    "MARUTI SUZUKI": "MARUTI.NS"
}

def resolve_symbol(user_input: str) -> Tuple[str, str]:
    """
    Resolves arbitrary user input into (clean_name, yfinance_ticker).
    
    Example:
        'reliance' -> ('RELIANCE', 'RELIANCE.NS')
        'nifty' -> ('NIFTY 50', '^NSEI')
        'banknifty' -> ('BANK NIFTY', '^NSEBANK')
        'TCS.NS' -> ('TCS', 'TCS.NS')
        '500325.BO' -> ('500325', '500325.BO')
    """
    raw = user_input.strip()
    upper = raw.upper()
    
    # 1. Check direct aliases
    if upper in ALIASES:
        clean_name = upper
        if clean_name in ["^NSEI", "NIFTY", "NIFTY50", "NIFTY 50"]:
            clean_name = "NIFTY 50"
        elif clean_name in ["^NSEBANK", "BANKNIFTY", "BANK NIFTY"]:
            clean_name = "BANK NIFTY"
        elif clean_name in ["^BSESN", "SENSEX"]:
            clean_name = "SENSEX"
        return clean_name, ALIASES[upper]
    
    # 2. Check DEFAULT_SYMBOLS
    if upper in DEFAULT_SYMBOLS:
        return upper, DEFAULT_SYMBOLS[upper]
    
    # 3. Already has suffix or prefix (.NS, .BO, ^)
    if upper.endswith(".NS") or upper.endswith(".BO") or upper.startswith("^"):
        clean_name = upper.replace(".NS", "").replace(".BO", "").replace("^", "")
        return clean_name, upper
    
    # 4. Clean symbols: remove spaces and special characters
    clean_sym = re.sub(r'[^A-Z0-9]', '', upper)
    
    # Check if cleaned version matches aliases
    if clean_sym in ALIASES:
        return clean_sym, ALIASES[clean_sym]
        
    # Default assumption: NSE listed stock
    return clean_sym, f"{clean_sym}.NS"

def get_clean_name(ticker: str) -> str:
    """Extract human-readable name from ticker."""
    for name, sym in ALIASES.items():
        if sym == ticker:
            return name
    return ticker.replace(".NS", "").replace(".BO", "").replace("^", "")
