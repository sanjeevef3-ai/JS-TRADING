"""
Comprehensive Indian Stocks, Indices & F&O Options Catalog
Provides search, auto-complete, and option contract generation for Portfolio Tracker.
"""

import re
import math
from typing import List, Dict, Any, Optional
from indian_market.options_engine import OptionsEngine

opt_engine = OptionsEngine()

STOCK_CATALOG = [
    # Major Indices
    {"symbol": "NIFTY", "name": "NIFTY 50 Index", "hindi": "निफ्टी 50", "ticker": "^NSEI", "type": "INDEX", "sector": "Benchmark", "lot_size": 25, "is_fno": True, "base_price": 25000.0},
    {"symbol": "BANKNIFTY", "name": "Bank Nifty Index", "hindi": "बैंक निफ्टी", "ticker": "^NSEBANK", "type": "INDEX", "sector": "Banking", "lot_size": 15, "is_fno": True, "base_price": 52000.0},
    {"symbol": "FINNIFTY", "name": "Nifty Financial Services", "hindi": "फिन निफ्टी", "ticker": "NIFTY_FIN_SERVICE.NS", "type": "INDEX", "sector": "Financials", "lot_size": 25, "is_fno": True, "base_price": 23500.0},
    {"symbol": "MIDCPNIFTY", "name": "Nifty Midcap Select", "hindi": "मिडकॅप निफ्टी", "ticker": "NIFTY_MIDCAP_100.NS", "type": "INDEX", "sector": "Midcap", "lot_size": 50, "is_fno": True, "base_price": 13000.0},
    {"symbol": "SENSEX", "name": "BSE Sensex 30", "hindi": "सेंसेक्स", "ticker": "^BSESN", "type": "INDEX", "sector": "Benchmark", "lot_size": 10, "is_fno": True, "base_price": 81500.0},

    # IT & Tech
    {"symbol": "TCS", "name": "Tata Consultancy Services", "hindi": "टीसीएस", "ticker": "TCS.NS", "type": "STOCK", "sector": "IT", "lot_size": 175, "is_fno": True, "base_price": 4150.0},
    {"symbol": "INFY", "name": "Infosys Ltd", "hindi": "इन्फोसिस", "ticker": "INFY.NS", "type": "STOCK", "sector": "IT", "lot_size": 400, "is_fno": True, "base_price": 1920.0},
    {"symbol": "HCLTECH", "name": "HCL Technologies", "hindi": "एचसीएल टेक", "ticker": "HCLTECH.NS", "type": "STOCK", "sector": "IT", "lot_size": 350, "is_fno": True, "base_price": 1820.0},
    {"symbol": "WIPRO", "name": "Wipro Ltd", "hindi": "विप्रो", "ticker": "WIPRO.NS", "type": "STOCK", "sector": "IT", "lot_size": 1500, "is_fno": True, "base_price": 540.0},
    {"symbol": "TECHM", "name": "Tech Mahindra", "hindi": "टेक महिंद्रा", "ticker": "TECHM.NS", "type": "STOCK", "sector": "IT", "lot_size": 600, "is_fno": True, "base_price": 1680.0},
    {"symbol": "LTIM", "name": "LTIMindtree", "hindi": "एलटीआईमाइंडट्री", "ticker": "LTIM.NS", "type": "STOCK", "sector": "IT", "lot_size": 150, "is_fno": True, "base_price": 6100.0},
    {"symbol": "PERSISTENT", "name": "Persistent Systems", "hindi": "पर्सिस्टेंट सिस्टम्स", "ticker": "PERSISTENT.NS", "type": "STOCK", "sector": "IT", "lot_size": 100, "is_fno": True, "base_price": 5400.0},
    {"symbol": "COFORGE", "name": "Coforge Ltd", "hindi": "कोफोर्ज", "ticker": "COFORGE.NS", "type": "STOCK", "sector": "IT", "lot_size": 150, "is_fno": True, "base_price": 7500.0},
    {"symbol": "TATAELXSI", "name": "Tata Elxsi", "hindi": "टाटा एलेक्सी", "ticker": "TATAELXSI.NS", "type": "STOCK", "sector": "IT", "lot_size": 100, "is_fno": True, "base_price": 7200.0},
    {"symbol": "INTELLECT", "name": "Intellect Design Arena", "hindi": "इंटेलेक्ट डिजाइन", "ticker": "INTELLECT.NS", "type": "STOCK", "sector": "Fintech", "lot_size": 50, "is_fno": False, "base_price": 920.0},

    # Banking & Financials
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "hindi": "एचडीएफसी बैंक", "ticker": "HDFCBANK.NS", "type": "STOCK", "sector": "Banking", "lot_size": 550, "is_fno": True, "base_price": 1680.0},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "hindi": "आईसीआईसीआई बैंक", "ticker": "ICICIBANK.NS", "type": "STOCK", "sector": "Banking", "lot_size": 700, "is_fno": True, "base_price": 1260.0},
    {"symbol": "SBIN", "name": "State Bank of India", "hindi": "एसबीआई (स्टेट बैंक)", "ticker": "SBIN.NS", "type": "STOCK", "sector": "Banking", "lot_size": 750, "is_fno": True, "base_price": 820.0},
    {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "hindi": "कोटक बैंक", "ticker": "KOTAKBANK.NS", "type": "STOCK", "sector": "Banking", "lot_size": 400, "is_fno": True, "base_price": 1850.0},
    {"symbol": "AXISBANK", "name": "Axis Bank Ltd", "hindi": "एक्सिस बैंक", "ticker": "AXISBANK.NS", "type": "STOCK", "sector": "Banking", "lot_size": 625, "is_fno": True, "base_price": 1190.0},
    {"symbol": "INDUSINDBK", "name": "IndusInd Bank", "hindi": "इंडसइंड बैंक", "ticker": "INDUSINDBK.NS", "type": "STOCK", "sector": "Banking", "lot_size": 500, "is_fno": True, "base_price": 1340.0},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance Ltd", "hindi": "बजाज फाइनेंस", "ticker": "BAJFINANCE.NS", "type": "STOCK", "sector": "NBFC", "lot_size": 125, "is_fno": True, "base_price": 7150.0},
    {"symbol": "BAJAJFINSV", "name": "Bajaj Finserv Ltd", "hindi": "बजाज फिनसर्व", "ticker": "BAJAJFINSV.NS", "type": "STOCK", "sector": "NBFC", "lot_size": 500, "is_fno": True, "base_price": 1820.0},
    {"symbol": "CHOLAFIN", "name": "Cholamandalam Investment", "hindi": "चोलामंडलम", "ticker": "CHOLAFIN.NS", "type": "STOCK", "sector": "NBFC", "lot_size": 625, "is_fno": True, "base_price": 1520.0},
    {"symbol": "MUTHOOTFIN", "name": "Muthoot Finance", "hindi": "मुथूट फाइनेंस", "ticker": "MUTHOOTFIN.NS", "type": "STOCK", "sector": "NBFC", "lot_size": 550, "is_fno": True, "base_price": 1960.0},
    {"symbol": "JIOFIN", "name": "Jio Financial Services", "hindi": "जियो फाइनेंशियल", "ticker": "JIOFIN.NS", "type": "STOCK", "sector": "Financials", "lot_size": 1000, "is_fno": False, "base_price": 325.0},
    {"symbol": "REC", "name": "REC Ltd", "hindi": "आरईसी", "ticker": "RECLTD.NS", "type": "STOCK", "sector": "PSU NBFC", "lot_size": 1000, "is_fno": True, "base_price": 540.0},
    {"symbol": "PFC", "name": "Power Finance Corp", "hindi": "पीएफसी", "ticker": "PFC.NS", "type": "STOCK", "sector": "PSU NBFC", "lot_size": 1300, "is_fno": True, "base_price": 490.0},
    {"symbol": "IREDA", "name": "Indian Renewable Energy Dev", "hindi": "इरेडा", "ticker": "IREDA.NS", "type": "STOCK", "sector": "Green Finance", "lot_size": 1000, "is_fno": False, "base_price": 225.0},

    # Energy, Oil & Gas
    {"symbol": "RELIANCE", "name": "Reliance Industries Ltd", "hindi": "रिलायंस इंडस्ट्रीज", "ticker": "RELIANCE.NS", "type": "STOCK", "sector": "Energy/Telecom", "lot_size": 250, "is_fno": True, "base_price": 2750.0},
    {"symbol": "ONGC", "name": "Oil & Natural Gas Corp", "hindi": "ओएनजीसी", "ticker": "ONGC.NS", "type": "STOCK", "sector": "Oil & Gas", "lot_size": 3850, "is_fno": True, "base_price": 290.0},
    {"symbol": "NTPC", "name": "NTPC Ltd", "hindi": "एनटीपीसी", "ticker": "NTPC.NS", "type": "STOCK", "sector": "Power", "lot_size": 1500, "is_fno": True, "base_price": 415.0},
    {"symbol": "POWERGRID", "name": "Power Grid Corp of India", "hindi": "पावर ग्रिड", "ticker": "POWERGRID.NS", "type": "STOCK", "sector": "Power", "lot_size": 2700, "is_fno": True, "base_price": 335.0},
    {"symbol": "TATAPOWER", "name": "Tata Power Company", "hindi": "टाटा पावर", "ticker": "TATAPOWER.NS", "type": "STOCK", "sector": "Power", "lot_size": 1350, "is_fno": True, "base_price": 440.0},
    {"symbol": "COALINDIA", "name": "Coal India Ltd", "hindi": "कोल इंडिया", "ticker": "COALINDIA.NS", "type": "STOCK", "sector": "Mining", "lot_size": 2100, "is_fno": True, "base_price": 495.0},
    {"symbol": "BPCL", "name": "Bharat Petroleum Corp", "hindi": "बीपीसीएल", "ticker": "BPCL.NS", "type": "STOCK", "sector": "Oil", "lot_size": 1800, "is_fno": True, "base_price": 345.0},
    {"symbol": "IOC", "name": "Indian Oil Corp", "hindi": "इंडियन ऑयल", "ticker": "IOC.NS", "type": "STOCK", "sector": "Oil", "lot_size": 4875, "is_fno": True, "base_price": 175.0},
    {"symbol": "GAIL", "name": "GAIL India Ltd", "hindi": "गेल", "ticker": "GAIL.NS", "type": "STOCK", "sector": "Gas", "lot_size": 2650, "is_fno": True, "base_price": 225.0},
    {"symbol": "SUZLON", "name": "Suzlon Energy", "hindi": "सुजलॉन", "ticker": "SUZLON.NS", "type": "STOCK", "sector": "Renewables", "lot_size": 1000, "is_fno": False, "base_price": 75.0},

    # Auto & Manufacturing
    {"symbol": "TATAMOTORS", "name": "Tata Motors Ltd", "hindi": "टाटा मोटर्स", "ticker": "TATAMOTORS.NS", "type": "STOCK", "sector": "Automobile", "lot_size": 550, "is_fno": True, "base_price": 940.0},
    {"symbol": "MARUTI", "name": "Maruti Suzuki India", "hindi": "मारुति सुजुकी", "ticker": "MARUTI.NS", "type": "STOCK", "sector": "Automobile", "lot_size": 50, "is_fno": True, "base_price": 12400.0},
    {"symbol": "M&M", "name": "Mahindra & Mahindra", "hindi": "महिंद्रा एंड महिंद्रा", "ticker": "M&M.NS", "type": "STOCK", "sector": "Automobile", "lot_size": 350, "is_fno": True, "base_price": 3150.0},
    {"symbol": "BAJAJ-AUTO", "name": "Bajaj Auto Ltd", "hindi": "बजाज ऑटो", "ticker": "BAJAJ-AUTO.NS", "type": "STOCK", "sector": "Automobile", "lot_size": 75, "is_fno": True, "base_price": 11800.0},
    {"symbol": "EICHERMOT", "name": "Eicher Motors (Royal Enfield)", "hindi": "आयशर मोटर्स", "ticker": "EICHERMOT.NS", "type": "STOCK", "sector": "Automobile", "lot_size": 150, "is_fno": True, "base_price": 4850.0},
    {"symbol": "HEROMOTOCO", "name": "Hero MotoCorp", "hindi": "हीरो मोटोकॉर्प", "ticker": "HEROMOTOCO.NS", "type": "STOCK", "sector": "Automobile", "lot_size": 150, "is_fno": True, "base_price": 5400.0},
    {"symbol": "BHARATFORG", "name": "Bharat Forge Ltd", "hindi": "भारत फोर्ज", "ticker": "BHARATFORG.NS", "type": "STOCK", "sector": "Auto Ancillary", "lot_size": 500, "is_fno": True, "base_price": 1540.0},
    {"symbol": "EXIDEIND", "name": "Exide Industries", "hindi": "एक्साइड इंडस्ट्रीज", "ticker": "EXIDEIND.NS", "type": "STOCK", "sector": "Batteries", "lot_size": 1200, "is_fno": True, "base_price": 510.0},

    # Metals & Mining
    {"symbol": "TATASTEEL", "name": "Tata Steel Ltd", "hindi": "टाटा स्टील", "ticker": "TATASTEEL.NS", "type": "STOCK", "sector": "Metals", "lot_size": 5500, "is_fno": True, "base_price": 165.0},
    {"symbol": "JSWSTEEL", "name": "JSW Steel Ltd", "hindi": "जेएसडब्ल्यू स्टील", "ticker": "JSWSTEEL.NS", "type": "STOCK", "sector": "Metals", "lot_size": 675, "is_fno": True, "base_price": 995.0},
    {"symbol": "HINDALCO", "name": "Hindalco Industries", "hindi": "हिंडाल्को", "ticker": "HINDALCO.NS", "type": "STOCK", "sector": "Metals", "lot_size": 1400, "is_fno": True, "base_price": 725.0},
    {"symbol": "VEDL", "name": "Vedanta Ltd", "hindi": "वेदांता", "ticker": "VEDL.NS", "type": "STOCK", "sector": "Metals", "lot_size": 2300, "is_fno": True, "base_price": 490.0},
    {"symbol": "JINDALSTEL", "name": "Jindal Steel & Power", "hindi": "जिंदल स्टील", "ticker": "JINDALSTEL.NS", "type": "STOCK", "sector": "Metals", "lot_size": 625, "is_fno": True, "base_price": 1020.0},
    {"symbol": "NATIONALUM", "name": "National Aluminium (NALCO)", "hindi": "नालको", "ticker": "NATIONALUM.NS", "type": "STOCK", "sector": "Metals", "lot_size": 3750, "is_fno": True, "base_price": 225.0},
    {"symbol": "SAIL", "name": "Steel Authority of India", "hindi": "सेल", "ticker": "SAIL.NS", "type": "STOCK", "sector": "Metals", "lot_size": 8000, "is_fno": True, "base_price": 138.0},

    # Defense & Capital Goods
    {"symbol": "BEL", "name": "Bharat Electronics Ltd", "hindi": "बीईएल (भारत इलेक्ट्रॉनिक्स)", "ticker": "BEL.NS", "type": "STOCK", "sector": "Defense", "lot_size": 2850, "is_fno": True, "base_price": 310.0},
    {"symbol": "HAL", "name": "Hindustan Aeronautics Ltd", "hindi": "एचएएल", "ticker": "HAL.NS", "type": "STOCK", "sector": "Defense", "lot_size": 300, "is_fno": True, "base_price": 4550.0},
    {"symbol": "LT", "name": "Larsen & Toubro Ltd", "hindi": "लार्सन एंड टुब्रो", "ticker": "LT.NS", "type": "STOCK", "sector": "Infrastructure", "lot_size": 150, "is_fno": True, "base_price": 3650.0},
    {"symbol": "BHEL", "name": "Bharat Heavy Electricals", "hindi": "भेल", "ticker": "BHEL.NS", "type": "STOCK", "sector": "Capital Goods", "lot_size": 2625, "is_fno": True, "base_price": 275.0},
    {"symbol": "MAZDOCK", "name": "Mazagon Dock Shipbuilders", "hindi": "माझगांव डॉक", "ticker": "MAZDOCK.NS", "type": "STOCK", "sector": "Defense", "lot_size": 125, "is_fno": False, "base_price": 4450.0},
    {"symbol": "COCHINSHIP", "name": "Cochin Shipyard", "hindi": "कोचीन शिपयार्ड", "ticker": "COCHINSHIP.NS", "type": "STOCK", "sector": "Defense", "lot_size": 200, "is_fno": False, "base_price": 1720.0},
    {"symbol": "RVNL", "name": "Rail Vikas Nigam Ltd", "hindi": "आरवीएनएल (रेल विकास)", "ticker": "RVNL.NS", "type": "STOCK", "sector": "Railways", "lot_size": 500, "is_fno": False, "base_price": 520.0},
    {"symbol": "IRFC", "name": "Indian Railway Finance Corp", "hindi": "आईआरएफसी", "ticker": "IRFC.NS", "type": "STOCK", "sector": "Railways", "lot_size": 1000, "is_fno": False, "base_price": 165.0},

    # Consumer, Retail & FMCG
    {"symbol": "ITC", "name": "ITC Ltd", "hindi": "आईटीसी", "ticker": "ITC.NS", "type": "STOCK", "sector": "FMCG", "lot_size": 1600, "is_fno": True, "base_price": 490.0},
    {"symbol": "HINDUNILVR", "name": "Hindustan Unilever Ltd", "hindi": "हिंदुस्तान यूनिलीवर", "ticker": "HINDUNILVR.NS", "type": "STOCK", "sector": "FMCG", "lot_size": 300, "is_fno": True, "base_price": 2780.0},
    {"symbol": "TITAN", "name": "Titan Company Ltd", "hindi": "टाइटन", "ticker": "TITAN.NS", "type": "STOCK", "sector": "Consumer", "lot_size": 175, "is_fno": True, "base_price": 3650.0},
    {"symbol": "TRENT", "name": "Trent Ltd (Westside/Zudio)", "hindi": "ट्रेंट (जूडियो)", "ticker": "TRENT.NS", "type": "STOCK", "sector": "Retail", "lot_size": 100, "is_fno": True, "base_price": 7950.0},
    {"symbol": "ZOMATO", "name": "Zomato Ltd (Blinkit)", "hindi": "जोमैटो", "ticker": "ZOMATO.NS", "type": "STOCK", "sector": "New-Age Tech", "lot_size": 2000, "is_fno": False, "base_price": 275.0},
    {"symbol": "VBL", "name": "Varun Beverages Ltd", "hindi": "वरुण बेवरेजेस", "ticker": "VBL.NS", "type": "STOCK", "sector": "FMCG", "lot_size": 500, "is_fno": True, "base_price": 595.0},
    {"symbol": "ASIANPAINT", "name": "Asian Paints Ltd", "hindi": "एशियन पेंट्स", "ticker": "ASIANPAINT.NS", "type": "STOCK", "sector": "Paints", "lot_size": 200, "is_fno": True, "base_price": 3120.0},
    {"symbol": "PIDILITIND", "name": "Pidilite Industries (Fevicol)", "hindi": "पिडिलाइट", "ticker": "PIDILITIND.NS", "type": "STOCK", "sector": "Chemicals", "lot_size": 250, "is_fno": True, "base_price": 3180.0},

    # Telecom, Adani & Others
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel Ltd", "hindi": "भारती एयरटेल", "ticker": "BHARTIARTL.NS", "type": "STOCK", "sector": "Telecom", "lot_size": 475, "is_fno": True, "base_price": 1680.0},
    {"symbol": "ADANIENT", "name": "Adani Enterprises Ltd", "hindi": "अडानी एंटरप्राइजेज", "ticker": "ADANIENT.NS", "type": "STOCK", "sector": "Conglomerate", "lot_size": 300, "is_fno": True, "base_price": 3150.0},
    {"symbol": "ADANIPORTS", "name": "Adani Ports & SEZ", "hindi": "अडानी पोर्ट्स", "ticker": "ADANIPORTS.NS", "type": "STOCK", "sector": "Infrastructure", "lot_size": 400, "is_fno": True, "base_price": 1450.0},
    {"symbol": "DLF", "name": "DLF Ltd", "hindi": "डीएलएफ", "ticker": "DLF.NS", "type": "STOCK", "sector": "Real Estate", "lot_size": 825, "is_fno": True, "base_price": 880.0},
    {"symbol": "SUNPHARMA", "name": "Sun Pharma Industries", "hindi": "सन फार्मा", "ticker": "SUNPHARMA.NS", "type": "STOCK", "sector": "Pharma", "lot_size": 350, "is_fno": True, "base_price": 1910.0},
    {"symbol": "CIPLA", "name": "Cipla Ltd", "hindi": "सिप्ला", "ticker": "CIPLA.NS", "type": "STOCK", "sector": "Pharma", "lot_size": 650, "is_fno": True, "base_price": 1580.0},
    {"symbol": "DRREDDY", "name": "Dr. Reddy's Laboratories", "hindi": "डॉ. रेड्डीज", "ticker": "DRREDDY.NS", "type": "STOCK", "sector": "Pharma", "lot_size": 125, "is_fno": True, "base_price": 6650.0}
]

SYMBOL_MAP = {s["symbol"]: s for s in STOCK_CATALOG}

def get_strike_step(spot: float) -> int:
    if spot >= 35000:
        return 100
    elif spot >= 10000:
        return 50
    elif spot >= 2500:
        return 50
    elif spot >= 1000:
        return 20
    elif spot >= 500:
        return 10
    else:
        return 5

def generate_option_contracts(underlying_sym: str, spot_price: float, strikes_count: int = 5) -> List[Dict[str, Any]]:
    """
    Generates realistic CE and PE option contracts around spot price with Black-Scholes Greeks.
    """
    item = SYMBOL_MAP.get(underlying_sym, {"symbol": underlying_sym, "lot_size": 25, "name": underlying_sym})
    lot_size = item.get("lot_size", 25)
    step = get_strike_step(spot_price)
    atm_strike = int(round(spot_price / step) * step)
    
    contracts = []
    
    # Generate strikes from (atm - step*strikes_count) to (atm + step*strikes_count)
    for i in range(-strikes_count, strikes_count + 1):
        k = atm_strike + (i * step)
        if k <= 0:
            continue
            
        is_atm = (i == 0)
        
        # Black-Scholes pricing
        ce_calc = opt_engine.black_scholes(spot_price, k, 4 / 365, 0.13, "CE")
        pe_calc = opt_engine.black_scholes(spot_price, k, 4 / 365, 0.13, "PE")
        
        ce_sym = f"{underlying_sym} {k} CE"
        pe_sym = f"{underlying_sym} {k} PE"
        
        # CALL Option
        contracts.append({
            "symbol": ce_sym,
            "display_name": f"{underlying_sym} {k} CALL (CE)",
            "underlying": underlying_sym,
            "type": "OPTION",
            "opt_type": "CE",
            "strike": k,
            "is_atm": is_atm,
            "cmp": round(float(ce_calc["price"]), 2),
            "lot_size": lot_size,
            "delta": round(float(ce_calc["delta"]), 2),
            "theta": round(float(ce_calc["theta"]), 2),
            "day_change": round((float(ce_calc["delta"]) * 2.5), 1)
        })
        
        # PUT Option
        contracts.append({
            "symbol": pe_sym,
            "display_name": f"{underlying_sym} {k} PUT (PE)",
            "underlying": underlying_sym,
            "type": "OPTION",
            "opt_type": "PE",
            "strike": k,
            "is_atm": is_atm,
            "cmp": round(float(pe_calc["price"]), 2),
            "lot_size": lot_size,
            "delta": round(float(pe_calc["delta"]), 2),
            "theta": round(float(pe_calc["theta"]), 2),
            "day_change": round((abs(float(pe_calc["delta"])) * -2.2), 1)
        })
        
    return contracts

def search_portfolio_assets(query: str = "", filter_type: str = "ALL", live_cache: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Unified search returning Stocks, Indices, and Option contracts matching user query.
    filter_type: 'ALL', 'STOCK', 'OPTION'
    """
    q = (query or "").strip().upper()
    filter_type = (filter_type or "ALL").strip().upper()
    results = []
    live_cache = live_cache or {}
    
    # Detect if user specifically queried an Option (e.g. contains CE, PE, CALL, PUT, or strike numbers)
    opt_match = re.search(r'\b(CE|PE|CALL|PUT)\b', q)
    strike_match = re.search(r'\b(\d{3,6})\b', q)
    
    is_option_specific = bool(opt_match or strike_match or filter_type == "OPTION")
    
    # 1. Search Stock Catalog
    if filter_type in ["ALL", "STOCK"]:
        matched_stocks = []
        for s in STOCK_CATALOG:
            sym = s["symbol"].upper()
            name = s["name"].upper()
            hindi = s.get("hindi", "").upper()
            sec = s.get("sector", "").upper()
            
            score = 0
            if not q:
                score = 1
            elif sym == q:
                score = 100
            elif sym.startswith(q):
                score = 80
            elif q in sym:
                score = 60
            elif q in name or q in hindi or q in sec:
                score = 40
                
            if score > 0:
                cached = live_cache.get(sym, {})
                cmp_val = cached.get("price") or s.get("base_price", 1000.0)
                chg_val = cached.get("p_change") or 0.85
                
                matched_stocks.append({
                    "symbol": s["symbol"],
                    "display_name": s["name"],
                    "hindi": s.get("hindi", ""),
                    "type": s["type"],
                    "sector": s["sector"],
                    "cmp": round(float(cmp_val), 2),
                    "day_change": round(float(chg_val), 2),
                    "lot_size": 1 if s["type"] == "STOCK" else s.get("lot_size", 25),
                    "is_fno": s.get("is_fno", False),
                    "relevance": score
                })
                
        matched_stocks.sort(key=lambda x: x["relevance"], reverse=True)
        results.extend(matched_stocks[:20])

    # 2. Options Contracts Generation & Search
    if filter_type in ["ALL", "OPTION"] or is_option_specific:
        # Determine candidate underlyings
        target_underlyings = []
        
        # Check if query starts with or mentions a known underlying
        for s in STOCK_CATALOG:
            if s.get("is_fno") and (s["symbol"] in q or q.startswith(s["symbol"])):
                target_underlyings.append(s)
                break
                
        if not target_underlyings:
            # Default to top liquid underlyings: NIFTY, BANKNIFTY, FINNIFTY, RELIANCE
            target_underlyings = [s for s in STOCK_CATALOG if s["symbol"] in ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE"]]
            
        opt_results = []
        for u in target_underlyings:
            sym = u["symbol"]
            cached = live_cache.get(sym, {})
            spot = float(cached.get("price") or u.get("base_price", 25000.0))
            
            contracts = generate_option_contracts(sym, spot, strikes_count=5)
            
            for c in contracts:
                # Filter by user query if specific
                score = 0
                c_sym = c["symbol"].upper()
                
                if not q or q in ["OPTION", "OPTIONS", "CE", "PE", "F&O"]:
                    score = 50 if c["is_atm"] else 20
                elif q in c_sym:
                    score = 90
                elif opt_match and opt_match.group(1) == c["opt_type"]:
                    if strike_match and str(c["strike"]) in q:
                        score = 100
                    elif strike_match:
                        score = 40
                    else:
                        score = 60 if c["is_atm"] else 30
                elif strike_match and str(c["strike"]) in q:
                    score = 80
                else:
                    if sym in q:
                        score = 40 if c["is_atm"] else 15
                        
                if score > 0:
                    c_copy = dict(c)
                    c_copy["relevance"] = score
                    opt_results.append(c_copy)
                    
        opt_results.sort(key=lambda x: (x["relevance"], -x.get("is_atm", 0)), reverse=True)
        results.extend(opt_results[:25])
        
    return results[:35]

def get_option_builder_data(underlying_sym: str = "NIFTY", live_cache: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Returns complete strike ladder for the interactive Option Builder modal.
    """
    sym = (underlying_sym or "NIFTY").strip().upper().replace(" 50", "").replace(" ", "")
    if sym not in SYMBOL_MAP:
        for k in SYMBOL_MAP:
            if k in sym or sym in k:
                sym = k
                break
    item = SYMBOL_MAP.get(sym, {"symbol": sym, "lot_size": 25, "name": sym, "base_price": 25000.0})
    live_cache = live_cache or {}
    cached = live_cache.get(sym, {})
    spot = float(cached.get("price") or item.get("base_price", 25000.0))
    lot_size = item.get("lot_size", 25)
    step = get_strike_step(spot)
    atm_strike = int(round(spot / step) * step)
    
    strikes = []
    for i in range(-5, 6):
        k = atm_strike + (i * step)
        if k <= 0:
            continue
        ce = opt_engine.black_scholes(spot, k, 4/365, 0.13, "CE")
        pe = opt_engine.black_scholes(spot, k, 4/365, 0.13, "PE")
        strikes.append({
            "strike": k,
            "is_atm": (i == 0),
            "diff_from_atm": i,
            "ce_symbol": f"{sym} {k} CE",
            "ce_price": round(float(ce["price"]), 2),
            "ce_delta": round(float(ce["delta"]), 2),
            "pe_symbol": f"{sym} {k} PE",
            "pe_price": round(float(pe["price"]), 2),
            "pe_delta": round(float(pe["delta"]), 2)
        })
        
    return {
        "underlying": sym,
        "name": item.get("name", sym),
        "spot": spot,
        "lot_size": lot_size,
        "step": step,
        "atm_strike": atm_strike,
        "strikes": strikes
    }
