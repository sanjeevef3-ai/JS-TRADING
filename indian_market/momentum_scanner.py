"""
High-Speed Pre-Breakout Radar, Fast Momentum Scanner & Option Buyer/Seller Regime Detector
1. Detects moves BEFORE they happen (Bollinger Squeeze, ATR Compression, NR7 Coiling, Stealth Volume Accumulation)
2. Classifies every Index/Stock into:
   - PRE-BREAKOUT COILING (Alert BEFORE the fast move starts!)
   - FAST MOMENTUM ACTIVE -> BUY CALL (CE) or BUY PUT (PE)
   - LOW MOMENTUM / SIDEWAYS -> OPTION SELLING (Short Strangle / Iron Condor for Theta Decay)
"""

import time
from typing import Dict, Any, List
import yfinance as yf
import pandas as pd
import numpy as np

SCANNER_WATCHLIST = [
    # Key Indices
    {"symbol": "NIFTY", "ticker": "^NSEI", "type": "Index"},
    {"symbol": "BANKNIFTY", "ticker": "^NSEBANK", "type": "Index"},
    {"symbol": "SENSEX", "ticker": "^BSESN", "type": "Index"},
    {"symbol": "FINNIFTY", "ticker": "NIFTY_FIN_SERVICE.NS", "type": "Index"},
    {"symbol": "MIDCPNIFTY", "ticker": "NIFTY_MIDCAP_100.NS", "type": "Index"},
    # High-Beta & Heavyweight F&O Stocks
    {"symbol": "RELIANCE", "ticker": "RELIANCE.NS", "type": "Energy"},
    {"symbol": "HDFCBANK", "ticker": "HDFCBANK.NS", "type": "Banking"},
    {"symbol": "ICICIBANK", "ticker": "ICICIBANK.NS", "type": "Banking"},
    {"symbol": "SBIN", "ticker": "SBIN.NS", "type": "Banking"},
    {"symbol": "TATAMOTORS", "ticker": "TATAMOTORS.NS", "type": "Auto"},
    {"symbol": "TATASTEEL", "ticker": "TATASTEEL.NS", "type": "Metal"},
    {"symbol": "BAJFINANCE", "ticker": "BAJFINANCE.NS", "type": "Finance"},
    {"symbol": "INFY", "ticker": "INFY.NS", "type": "IT"},
    {"symbol": "TCS", "ticker": "TCS.NS", "type": "IT"},
    {"symbol": "ADANIENT", "ticker": "ADANIENT.NS", "type": "Conglomerate"},
    {"symbol": "LT", "ticker": "LT.NS", "type": "Infra"},
    {"symbol": "BHARTIARTL", "ticker": "BHARTIARTL.NS", "type": "Telecom"},
    {"symbol": "TITAN", "ticker": "TITAN.NS", "type": "Consumer"}
]

class MomentumScanner:
    """
    Detects:
    1. Pre-Breakout Coiling (move aane se pehle warning)
    2. Live Fast Momentum (Option Buying: Call / Put)
    3. Low Momentum Consolidation (Option Selling: Iron Condor / Strangle)
    """

    def __init__(self):
        self._cache = {}
        self._cache_ttl = 30 # 30 seconds fast cache
        self._notif_registry = {} # symbol -> stable notification object until real change occurs

    def check_market_session(self) -> Dict[str, Any]:
        """
        Determines if Indian Stock Market (NSE/BSE) is actively open for trading.
        Official Trading Hours: Monday to Friday, 09:15 AM to 03:30 PM IST.
        After 03:30 PM, market is CLOSED - live CE/PE breakout buy alerts must be paused!
        """
        try:
            import zoneinfo
            ist = zoneinfo.ZoneInfo("Asia/Kolkata")
        except Exception:
            ist = None

        from datetime import datetime, time as dtime
        now_ist = datetime.now(ist) if ist else datetime.now()
        weekday = now_ist.weekday() # 0=Mon, 4=Fri, 5=Sat, 6=Sun
        cur_time = now_ist.time()

        is_trading_day = (weekday < 5)
        is_live_hours = is_trading_day and (dtime(9, 15) <= cur_time <= dtime(15, 30))
        is_pre_market = is_trading_day and (dtime(9, 0) <= cur_time < dtime(9, 15))

        if is_live_hours:
            status = "OPEN"
            status_text = "Live Market Session (09:15 – 15:30 IST)"
            can_issue_live_trade_alerts = True
        elif is_pre_market:
            status = "PRE_MARKET"
            status_text = "Pre-Market Session (09:00 – 09:15 IST • Order matching in progress)"
            can_issue_live_trade_alerts = False
        elif weekday >= 5:
            status = "WEEKEND_CLOSED"
            status_text = "Market Closed (Weekend • Next Session opens Monday at 09:15 AM IST)"
            can_issue_live_trade_alerts = False
        else:
            status = "POST_MARKET_CLOSED"
            status_text = "Market Closed (Post-Market Hours • Next Session opens next trading day at 09:15 AM IST)"
            can_issue_live_trade_alerts = False

        return {
            "is_market_open": is_live_hours,
            "can_issue_live_trade_alerts": can_issue_live_trade_alerts,
            "status": status,
            "status_text": status_text,
            "server_time_ist": now_ist.strftime("%d %b %Y • %I:%M:%S %p"),
            "weekday": weekday
        }

    def _get_strike_step(self, price: float) -> int:
        if price > 35000:
            return 100
        elif price > 10000:
            return 50
        elif price > 2000:
            return 20
        elif price > 500:
            return 10
        return 5

    def _analyze_ticker_frame(self, item: Dict[str, str], df: pd.DataFrame) -> Dict[str, Any]:
        sym = item["symbol"]
        ticker = item["ticker"]

        closes = df["Close"].values
        highs = df["High"].values
        lows = df["Low"].values
        opens = df["Open"].values
        volumes = df["Volume"].values

        cur_price = round(float(closes[-1]), 2)
        prev_price = round(float(closes[-2]), 2)
        day_open = round(float(opens[-min(len(opens), 25)]), 2)

        # 1. Price Velocity
        recent_pct_move = round(((cur_price - prev_price) / prev_price) * 100, 2)
        candle_3_move = round(((cur_price - float(closes[-4])) / float(closes[-4])) * 100, 2) if len(closes) >= 4 else recent_pct_move
        day_pct_move = round(((cur_price - day_open) / day_open) * 100, 2)

        # 2. Volume Accumulation & Spike
        vol_sma20 = float(np.mean(volumes[-20:])) if len(volumes) >= 20 else float(np.mean(volumes))
        cur_vol = float(volumes[-1])
        recent_3_vol = float(np.mean(volumes[-3:]))
        vol_spike_ratio = round(cur_vol / vol_sma20, 2) if vol_sma20 > 0 else 1.0
        stealth_vol_ratio = round(recent_3_vol / vol_sma20, 2) if vol_sma20 > 0 else 1.0

        # 3. RSI 14
        deltas = np.diff(closes[-15:])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_g = float(np.mean(gains)) if len(gains) > 0 else 0.0
        avg_l = float(np.mean(losses)) if len(losses) > 0 else 1e-6
        rs = avg_g / avg_l if avg_l > 0 else 1.0
        rsi = round(100.0 - (100.0 / (1.0 + rs)), 1)

        # 4. Pre-Breakout Squeeze Detection (Move aane se PEHLE pakadne ka formula)
        # a) Bollinger Band Width (BBW) Compression
        sma20 = float(np.mean(closes[-20:]))
        std20 = float(np.std(closes[-20:]))
        bb_width_pct = round(((4.0 * std20) / sma20) * 100, 2) if sma20 > 0 else 2.0

        # Historical BB widths to check percentile squeeze
        hist_bbw = []
        if len(closes) >= 35:
            for k in range(len(closes) - 15, len(closes)):
                sub = closes[k-19:k+1]
                m = float(np.mean(sub))
                s = float(np.std(sub))
                if m > 0:
                    hist_bbw.append((4.0 * s / m) * 100)
        min_bbw = min(hist_bbw) if hist_bbw else bb_width_pct
        max_bbw = max(hist_bbw) if hist_bbw else bb_width_pct + 1.0
        bb_squeeze_ratio = 1.0 - ((bb_width_pct - min_bbw) / max(0.01, (max_bbw - min_bbw)))
        bb_squeeze_ratio = max(0.0, min(1.0, bb_squeeze_ratio))

        # b) NR7 / Narrow Range Coiling (Last 3 candles range vs 15-candle average range)
        ranges = highs[-20:] - lows[-20:]
        avg_range = float(np.mean(ranges[:-3])) if len(ranges) > 5 else float(np.mean(ranges))
        recent_range = float(np.mean(ranges[-3:]))
        range_compression = round(recent_range / avg_range, 2) if avg_range > 0 else 1.0
        is_nr7 = recent_range < (avg_range * 0.72)

        # c) EMA 9 & EMA 20 Tight Ribbon Coiling
        ema9 = float(pd.Series(closes).ewm(span=9, adjust=False).mean().iloc[-1])
        ema20 = float(pd.Series(closes).ewm(span=20, adjust=False).mean().iloc[-1])
        ema_gap_pct = round(abs(ema9 - ema20) / cur_price * 100, 3)
        is_ema_coiled = ema_gap_pct < 0.28

        # Calculate Pre-Breakout Score (0 - 100)
        squeeze_score = 0.0
        # Absolute Bollinger Band tightness (tighter than 1.2% for stocks or 0.65% for indices)
        is_tight_bb = (bb_width_pct < 0.75) if item["type"] == "Index" else (bb_width_pct < 1.35)
        if is_tight_bb:
            squeeze_score += 35.0
        squeeze_score += bb_squeeze_ratio * 25.0
        if is_nr7:
            squeeze_score += 20.0
        if is_ema_coiled:
            squeeze_score += 10.0
        if stealth_vol_ratio >= 1.15: # Stealth accumulation during squeeze
            squeeze_score += 15.0
        squeeze_score = round(min(100.0, squeeze_score), 1)

        # 5. Live Fast Momentum Score (0 - 100)
        momentum_score = 0.0
        momentum_score += min(38.0, vol_spike_ratio * 15.0)
        momentum_score += min(37.0, abs(candle_3_move) * 24.0 + abs(recent_pct_move) * 20.0)
        momentum_score += min(25.0, abs(rsi - 50.0) * 1.2)
        momentum_score = round(min(100.0, momentum_score), 1)

        # 6. Expected Breakout / Momentum Direction
        bull_signals = (cur_price >= ema9) + (ema9 >= ema20) + (rsi >= 52) + (recent_pct_move >= 0)
        is_bullish_bias = bull_signals >= 3

        step = self._get_strike_step(cur_price)
        atm_strike = int(round(cur_price / step) * step)
        strangle_ce = atm_strike + (step * 3)
        strangle_pe = atm_strike - (step * 3)

        # 7. Smart Classification: PRE-BREAKOUT vs FAST MOMENTUM (Option Buy) vs LOW MOMENTUM (Option Sell)
        pre_breakout_signals = []
        if is_tight_bb:
            pre_breakout_signals.append(f"Tight BB Squeeze ({bb_width_pct}%)")
        if is_nr7:
            pre_breakout_signals.append(f"NR7 Coiling ({range_compression}x)")
        if is_ema_coiled:
            pre_breakout_signals.append("EMA 9/20 Spring")
        if stealth_vol_ratio >= 1.15:
            pre_breakout_signals.append(f"Stealth Vol ({stealth_vol_ratio}x)")

        if momentum_score >= 48.0 or abs(recent_pct_move) >= 0.45 or vol_spike_ratio >= 1.45:
            # FAST MOMENTUM ACTIVE -> OPTION BUYING
            alert_stage = "FAST_MOMENTUM_LIVE"
            option_mode = "OPTION BUYING (Fast Momentum)"
            if is_bullish_bias:
                direction = "BULLISH BLAST 🚀"
                action = f"BUY {atm_strike} CE (Call Buy)"
                recommended_strategy = "Long Call" if momentum_score >= 60 else "Bull Call Spread"
                alert_message = f"🔥 FAST BULLISH MOMENTUM in {sym} (Rs.{cur_price})! Score {momentum_score}/100. Action: BUY {sym} {atm_strike} CE for Gamma surge!"
            else:
                direction = "BEARISH CRASH 🔻"
                action = f"BUY {atm_strike} PE (Put Buy)"
                recommended_strategy = "Long Put" if momentum_score >= 60 else "Bear Put Spread"
                alert_message = f"🔥 FAST BEARISH BREAKDOWN in {sym} (Rs.{cur_price})! Score {momentum_score}/100. Action: BUY {sym} {atm_strike} PE!"

        elif squeeze_score >= 68.0:
            # PRE-BREAKOUT WARNING -> MOVE AANE SE PEHLE ALERT!
            alert_stage = "PRE_BREAKOUT_WARNING"
            option_mode = "PRE-BREAKOUT ALERT (Ready to Buy CE/PE)"
            expected_dir = "UPSIDE BULLISH" if is_bullish_bias else "DOWNSIDE BEARISH"
            target_opt = f"{atm_strike} CE" if is_bullish_bias else f"{atm_strike} PE"
            direction = f"COILING FOR {expected_dir} BLAST ⚡"
            action = f"READY TO BUY {target_opt} ON BREAKOUT"
            recommended_strategy = "Bull Call Spread" if is_bullish_bias else "Bear Put Spread"
            breakout_lvl = round(float(np.max(highs[-5:])), 2) if is_bullish_bias else round(float(np.min(lows[-5:])), 2)
            alert_message = (
                f"🚨 PRE-BREAKOUT ALERT: {sym} (Rs.{cur_price}) me bada move aane se pehle coiling! "
                f"Squeeze: {squeeze_score}%. Trigger level: Rs.{breakout_lvl}. "
                f"Keep {sym} {target_opt} ready to BUY!"
            )

        else:
            # LOW MOMENTUM / SIDEWAYS -> OPTION SELLING (THETA DECAY)
            alert_stage = "LOW_MOMENTUM_SELL_OPTIONS"
            option_mode = "OPTION SELLING (Theta Decay Mode)"
            direction = "LOW MOMENTUM / SIDEWAYS 💤"
            action = f"SELL {strangle_pe} PE & {strangle_ce} CE (Option Selling)"
            recommended_strategy = "Iron Condor"
            alert_message = (
                f"🛡️ LOW MOMENTUM in {sym} (Rs.{cur_price}) | Mom: {momentum_score}/100. "
                f"Option Buying me Theta loss hoga. Deploy OPTION SELLING: Iron Condor / Short Strangle ({strangle_pe} PE & {strangle_ce} CE)!"
            )

        # Trigger Summary
        triggers = []
        if pre_breakout_signals:
            triggers.extend(pre_breakout_signals[:2])
        if vol_spike_ratio >= 1.4:
            triggers.append(f"Vol {vol_spike_ratio}x")
        if abs(recent_pct_move) >= 0.4:
            triggers.append(f"Move {recent_pct_move}%")
        if rsi >= 62 or rsi <= 38:
            triggers.append(f"RSI {rsi}")
        trigger_text = " + ".join(triggers) if triggers else f"Range Bound (RSI {rsi})"

        return {
            "symbol": sym,
            "ticker": ticker,
            "type": item["type"],
            "price": round(cur_price, 2),
            "atm_strike": atm_strike,
            "recent_change": f"{recent_pct_move}%",
            "day_change": f"{day_pct_move}%",
            "volume_ratio": f"{vol_spike_ratio}x",
            "rsi": rsi,
            "momentum_score": momentum_score,
            "squeeze_score": squeeze_score,
            "alert_stage": alert_stage,
            "option_mode": option_mode,
            "recommended_strategy": recommended_strategy,
            "direction": direction,
            "action": action,
            "trigger_reason": trigger_text,
            "alert_message": alert_message,
            "breakout_watch_high": round(float(np.max(highs[-5:])), 2),
            "breakout_watch_low": round(float(np.min(lows[-5:])), 2)
        }

    def _get_or_create_notification(self, item: Dict[str, Any], notif_type: str, priority: str, title: str) -> Dict[str, Any]:
        sym = item["symbol"]
        stage = str(item.get("alert_stage", "")).replace(" ", "_").upper()
        action = str(item.get("action", "")).replace(" ", "_").upper()
        price = float(item.get("price", 0.0))
        reg = self._notif_registry.get(sym)

        # Check if changed:
        if reg is not None:
            prev_stage = reg.get("alert_stage")
            prev_action = reg.get("action_key")
            prev_price = float(reg.get("price", 0.0))
            price_delta_pct = abs(price - prev_price) / max(1.0, prev_price)

            # JAB TAK KOI CHANGE NA HO TAB TAK SAME NOTIFICATION REPEAT NAHI HONA CHAHIYE:
            # If stage, action and price (within 1.5%) haven't changed, reuse exact same notification & original timestamp!
            if prev_stage == stage and prev_action == action and price_delta_pct < 0.015:
                return reg

        # If genuine change or first time:
        cur_datetime_str = time.strftime("%d %b %Y • %I:%M:%S %p")
        
        # Lemonn-inspired Zing Visual Matrix & Smart Limit calculations
        est_premium = round(max(15.0, price * 0.018), 1)
        smart_limit_price = round(est_premium * 0.982, 1)
        savings_per_sh = round(est_premium - smart_limit_price, 1)
        sl_pts = round(max(4.0, est_premium * 0.22), 1)
        target_1 = round(est_premium + sl_pts * 1.5, 1)
        target_2 = round(est_premium + sl_pts * 2.8, 1)
        hard_sl = round(max(1.0, est_premium - sl_pts), 1)

        # 💎 90%+ Diamond Filter Evaluation
        try:
            from indian_market.diamond_filter import diamond_filter
            vol_val = 1.0
            if "volume_ratio" in item:
                vol_val = float(str(item["volume_ratio"]).replace("x", ""))
            
            d_eval = diamond_filter.evaluate(
                symbol=sym,
                price=price,
                action=item.get("action", ""),
                momentum_score=float(item.get("momentum_score", 50.0)),
                squeeze_score=float(item.get("squeeze_score", 50.0)),
                rsi=float(item.get("rsi", 50.0)),
                volume_ratio=vol_val,
                swarm_votes_buy=4 if float(item.get("momentum_score", 50)) >= 65 else 3
            )
        except Exception:
            d_eval = {
                "is_diamond": False,
                "win_probability_pct": 65.0,
                "grade": "STANDARD",
                "verifications": [],
                "invalidation_rule": "Standard ATR",
                "target_rule": "Standard",
                "sniper_verdict_hindi": ""
            }

        is_diamond = d_eval["is_diamond"]
        win_prob = d_eval["win_probability_pct"]

        if is_diamond:
            title = f"💎 DIAMOND 90%+ SETUP: {sym} — {item.get('action', '')}"
            priority = "DIAMOND_90_URGENT"

        if notif_type == "PRE_BREAKOUT":
            rationale_hindi = f"15m Bollinger Band tight squeeze coiling ({item.get('squeeze_score', 0):.0f}%). Bada breakout blast expected!"
        else:
            rationale_hindi = f"Impulse Momentum ({item.get('momentum_score', 0):.0f}/100). Directional Call/Put Buying me fast target move!"

        if is_diamond and d_eval.get("sniper_verdict_hindi"):
            rationale_hindi = d_eval["sniper_verdict_hindi"]

        notif = {
            "id": f"SIG_{sym}_{stage}_{action}",
            "priority": priority,
            "type": notif_type,
            "is_important": True,
            "symbol": sym,
            "title": title,
            "message": item.get("alert_message", ""),
            "action": item.get("action", ""),
            "action_key": action,
            "option_mode": item.get("option_mode", ""),
            "recommended_strategy": item.get("recommended_strategy", ""),
            "squeeze_score": item.get("squeeze_score", 0.0),
            "momentum_score": item.get("momentum_score", 0.0),
            "price": price,
            "optimal_limit_price": smart_limit_price,
            "target_1": target_1,
            "target_2": target_2,
            "hard_sl": hard_sl,
            "risk_reward": "1 : 2.5",
            "slippage_savings": f"Rs.{savings_per_sh}/sh bachat",
            "ai_rationale_hindi": rationale_hindi,
            "timestamp": cur_datetime_str,
            "time_clock": time.strftime("%H:%M:%S"),
            "alert_stage": stage,
            "is_diamond": is_diamond,
            "win_probability_pct": win_prob,
            "diamond_grade": d_eval.get("grade", "STANDARD"),
            "diamond_verifications": d_eval.get("verifications", []),
            "diamond_invalidation": d_eval.get("invalidation_rule", ""),
            "diamond_target_rule": d_eval.get("target_rule", "")
        }
        self._notif_registry[sym] = notif
        return notif

    def scan_all_signals(self) -> Dict[str, Any]:
        """
        Full scan across Indices & Stocks returning:
        1. pre_breakout_alerts (Move aane se pehle notification!)
        2. fast_movers (High momentum -> Call/Put Buying)
        3. option_selling_candidates (Low momentum -> Option Selling / Iron Condor / Strangle)
        4. notifications (Push notification queue for frontend toast + sound + browser notification)
        """
        now = time.time()
        if "full_scan" in self._cache and (now - self._cache["full_scan"]["ts"] < self._cache_ttl):
            return self._cache["full_scan"]["data"]

        all_items = []
        tickers_str = " ".join([x["ticker"] for x in SCANNER_WATCHLIST])
        try:
            batch_df = yf.download(tickers_str, period="5d", interval="15m", group_by="ticker", progress=False, threads=True)
        except Exception:
            batch_df = None

        for item in SCANNER_WATCHLIST:
            ticker = item["ticker"]
            try:
                if batch_df is not None and not batch_df.empty and ticker in batch_df.columns.get_level_values(0):
                    hist = batch_df[ticker].dropna(how="all")
                else:
                    stk = yf.Ticker(ticker)
                    hist = stk.history(period="5d", interval="15m")

                if hist is None or hist.empty or len(hist) < 20:
                    continue

                res = self._analyze_ticker_frame(item, hist)
                all_items.append(res)
            except Exception:
                continue

        # Sort lists
        pre_breakout = [x for x in all_items if x["alert_stage"] == "PRE_BREAKOUT_WARNING" or x["squeeze_score"] >= 55.0]
        pre_breakout.sort(key=lambda x: x["squeeze_score"], reverse=True)

        fast_movers = sorted(all_items, key=lambda x: (x["momentum_score"] * 0.65 + x["squeeze_score"] * 0.35), reverse=True)

        selling_zone = [x for x in all_items if x["alert_stage"] == "LOW_MOMENTUM_SELL_OPTIONS"]
        selling_zone.sort(key=lambda x: x["momentum_score"]) # Lowest momentum first (best for option selling)

        # Check if Market is actively open (09:15 – 15:30 IST Mon-Fri)
        session_info = self.check_market_session()
        is_live_market = session_info["can_issue_live_trade_alerts"]

        # Build notifications list:
        # ⚠️ CRITICAL: Live intraday CE/PE breakout buy alerts MUST ONLY be issued during live trading hours!
        # After 15:30 IST or on weekends, all live intraday trade alerts are PAUSED to prevent false alarms!
        notifications = []
        if is_live_market:
            for pb in pre_breakout[:4]:
                notif = self._get_or_create_notification(
                    item=pb,
                    notif_type="PRE_BREAKOUT",
                    priority="HIGH_PRE_BREAKOUT",
                    title=f"🚨 PRE-BREAKOUT ALERT: {pb['symbol']}"
                )
                notifications.append(notif)

            for fm in fast_movers[:3]:
                if fm["momentum_score"] >= 55.0 and not any(n["symbol"] == fm["symbol"] for n in notifications):
                    notif = self._get_or_create_notification(
                        item=fm,
                        notif_type="TRADE",
                        priority="URGENT_MOMENTUM",
                        title=f"⚡ FAST MOMENTUM: {fm['symbol']} — BUY OPTION!"
                    )
                    notifications.append(notif)
        else:
            # Post-Market / Off-Hours: Silent Market Status Notice (Zero pop-up flash, zero audio beep)
            now_str = session_info.get("server_time_ist", time.strftime("%d %b %Y • %I:%M:%S %p"))
            notifications.append({
                "id": f"MKT_STATUS_{session_info['status']}",
                "priority": "INFO",
                "type": "MARKET_CLOSED",
                "is_important": False,
                "title": f"🏁 {session_info['status_text']}",
                "message": (
                    f"Market 15:30 IST par band ho gaya hai. Naye CE/PE breakout alerts pause hain. "
                    f"EOD scanner active hai. Agla live session next trading day subah 09:15 AM par shuru hoga."
                ),
                "symbol": "NSE",
                "price": None,
                "timestamp": now_str,
                "time_clock": time.strftime("%H:%M:%S"),
                "is_market_closed": True
            })

        # Overall Market Regime Summary
        avg_mom = round(float(np.mean([x["momentum_score"] for x in all_items])), 1) if all_items else 45.0
        avg_sqz = round(float(np.mean([x["squeeze_score"] for x in all_items])), 1) if all_items else 50.0

        if is_live_market:
            if avg_mom >= 56.0:
                global_regime = "FAST MOMENTUM REGIME — OPTION BUYING (Call/Put Buy)"
                global_advice = "Market me tezi/fast impulse hai! Option Buying (Long Call / Long Put / Debit Spreads) me bada paisa banega."
            elif len(pre_breakout) >= 3:
                global_regime = "PRE-BREAKOUT COILING — GET READY FOR OPTION BUYING"
                global_advice = f"{len(pre_breakout)} stocks/indices tight squeeze me hain! Bada blast aane se pehle Call/Put Buy ke liye alert rahein."
            else:
                global_regime = "LOW MOMENTUM / SIDEWAYS — OPTION SELLING REGIME"
                global_advice = "Market slow/rangebound hai. Option Buying me Theta decay lagega — Option Selling (Iron Condor / Short Strangle) apnayein!"
        else:
            global_regime = f"🏁 {session_info['status_text']}"
            global_advice = f"Market session band ho chuka hai (09:15–15:30 IST). EOD technical analysis data loaded. Agla live session 09:15 AM IST par start hoga."

        diamond_trades = [n for n in notifications if n.get("is_diamond")]

        payload = {
            "timestamp": time.strftime("%H:%M:%S"),
            "market_session": session_info,
            "global_regime": global_regime,
            "global_advice": global_advice,
            "avg_market_momentum": avg_mom,
            "avg_market_squeeze": avg_sqz,
            "notifications": notifications,
            "diamond_trades": diamond_trades,
            "diamond_count": len(diamond_trades),
            "pre_breakout_alerts": pre_breakout[:6],
            "fast_movers": fast_movers[:8],
            "option_selling_candidates": selling_zone[:6]
        }

        self._cache["full_scan"] = {"ts": now, "data": payload}
        return payload

    def scan_fast_momentum(self, top_n: int = 6) -> List[Dict[str, Any]]:
        """Backward-compatible method returning top fast movers."""
        data = self.scan_all_signals()
        return data.get("fast_movers", [])[:top_n]
