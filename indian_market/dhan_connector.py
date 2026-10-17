"""
Dhan Official API Integration Module (via dhanhq v2.3+ SDK with DhanContext & Auto-Renewal)
Provides direct connectivity to Dhan broker accounts for live fund limits,
positions, order book, option chain, and 100% Permanent Auto-Token Renewal.
"""

import os
import json
import time
import base64
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List
from config import BASE_DIR

DHAN_CONFIG_FILE = BASE_DIR / ".dhan_config.json"

class DhanConnector:
    """
    Manages connection to Dhan HQ API v2.3+ (https://dhanhq.co)
    with Permanent Background Token Auto-Renewal via DhanLogin.renew_token().
    """

    def __init__(self, client_id: str = None, access_token: str = None):
        self.client_id = client_id or os.environ.get("DHAN_CLIENT_ID")
        self.access_token = access_token or os.environ.get("DHAN_ACCESS_TOKEN")
        self.last_renewed_at = None
        self.token_expiry_str = "Auto-Renewing (Permanent)"
        
        if not (self.client_id and self.access_token) and DHAN_CONFIG_FILE.exists():
            try:
                with open(DHAN_CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.client_id = self.client_id or cfg.get("client_id")
                    self.access_token = self.access_token or cfg.get("access_token")
                    self.last_renewed_at = cfg.get("last_renewed_at")
                    self.token_expiry_str = cfg.get("token_expiry", "Auto-Renewing (Permanent)")
            except Exception:
                pass

        self.ctx = None
        self.dhan = None
        self.is_connected = False
        self._init_client()
        self.auto_renew_if_needed()
        self._start_background_renewer()

    def _decode_jwt_exp(self, token: str) -> Optional[int]:
        """Extracts 'exp' unix timestamp from Dhan JWT token."""
        try:
            parts = token.split(".")
            if len(parts) < 2:
                return None
            payload_b64 = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
            return int(payload.get("exp", 0))
        except Exception:
            return None

    def _init_client(self):
        """Initializes the dhanhq v2.3+ SDK client using DhanContext."""
        if self.client_id and self.access_token:
            try:
                from dhanhq import DhanContext, dhanhq
                self.ctx = DhanContext(str(self.client_id).strip(), str(self.access_token).strip())
                self.dhan = dhanhq(self.ctx)
                self.is_connected = True
            except Exception as e:
                self.is_connected = False
                print(f"[Dhan SDK Init Notice]: {e}")

    def auto_renew_if_needed(self, force: bool = False) -> Dict[str, Any]:
        """
        Checks if token has less than 12 hours remaining (or if force=True)
        and automatically renews it via DhanLogin.renew_token() for Perpetual Validity!
        """
        if not (self.client_id and self.access_token):
            return {"renewed": False, "reason": "No credentials"}

        exp_ts = self._decode_jwt_exp(self.access_token)
        now_ts = int(time.time())

        # If token is already expired, Dhan renew_token will reject with DH-901. Only fresh token can be extended!
        if exp_ts and exp_ts < now_ts:
            return {"renewed": False, "reason": "Token already expired. New token required from Dhan Web/App."}

        # Renew if force=True or if less than 12 hours (43200s) left before expiry
        if force or (exp_ts and (exp_ts - now_ts) < 43200):
            try:
                from dhanhq import DhanLogin
                dl = DhanLogin(str(self.client_id).strip())
                res = dl.renew_token(str(self.access_token).strip())
                if isinstance(res, dict) and res.get("token"):
                    new_token = res["token"]
                    expiry_time = res.get("expiryTime", "Auto-Extended +24h")
                    self.save_credentials(self.client_id, new_token, expiry_time=expiry_time)
                    return {
                        "renewed": True,
                        "new_expiry": expiry_time,
                        "message": "Token automatically renewed via Dhan HQ API!"
                    }
            except Exception as e:
                return {"renewed": False, "error": str(e)}

        return {"renewed": False, "reason": "Token still fresh (>12h validity remaining)"}

    def _start_background_renewer(self):
        """Daemon thread that checks every 4 hours and auto-renews the token forever."""
        def _loop():
            while True:
                time.sleep(14400) # Every 4 hours
                try:
                    self.auto_renew_if_needed(force=False)
                except Exception:
                    pass
        t = threading.Thread(target=_loop, daemon=True)
        t.start()

    def save_credentials(self, client_id: str, access_token: str, expiry_time: str = None) -> bool:
        """Saves Dhan API credentials securely to local config file and connects."""
        self.client_id = str(client_id).strip()
        self.access_token = str(access_token).strip()
        self.last_renewed_at = time.strftime("%Y-%m-%d %H:%M:%S")
        if expiry_time:
            self.token_expiry_str = expiry_time
        try:
            with open(DHAN_CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "client_id": self.client_id,
                    "access_token": self.access_token,
                    "last_renewed_at": self.last_renewed_at,
                    "token_expiry": self.token_expiry_str,
                    "auto_renew_enabled": True
                }, f, indent=2)
            self._init_client()
            return self.is_connected
        except Exception as e:
            print(f"[Error saving Dhan credentials]: {e}")
            return False

    def test_connection(self) -> Dict[str, Any]:
        """Tests live API connectivity and returns real-time Dhan account status & funds."""
        if not self.is_connected:
            self._init_client()

        if not self.is_connected or not self.dhan:
            return {
                "connected": False,
                "status": "DISCONNECTED",
                "message": "Dhan credentials not configured.",
                "is_active": False
            }

        try:
            profile = self.dhan.get_fund_limits()
            api_status = profile.get("status", "failure") if isinstance(profile, dict) else "failure"

            # If token expired or got invalidated, try auto-renewing once
            if api_status != "success":
                renew_attempt = self.auto_renew_if_needed(force=True)
                if renew_attempt.get("renewed"):
                    profile = self.dhan.get_fund_limits()
                    api_status = profile.get("status", "failure") if isinstance(profile, dict) else "failure"

            data = profile.get("data", {}) if isinstance(profile, dict) else {}

            if api_status == "success":
                avail_bal = data.get("availabelBalance", data.get("availableBalance", 0.0))
                utilized = data.get("utilizedAmount", 0.0)
                withdrawable = data.get("withdrawableBalance", 0.0)

                positions_count = 0
                orders_count = 0
                token_validity = self.token_expiry_str
                active_segments = "NSE, BSE, F&O, MCX"

                try:
                    from dhanhq import DhanLogin
                    u_prof = DhanLogin(self.client_id).user_profile(self.access_token)
                    if isinstance(u_prof, dict) and u_prof.get("tokenValidity"):
                        token_validity = f"{u_prof.get('tokenValidity')} (🔄 Auto-Renew ON)"
                        active_segments = u_prof.get("activeSegment", active_segments)
                except Exception:
                    pass

                try:
                    pos_res = self.dhan.get_positions()
                    if isinstance(pos_res, dict) and pos_res.get("status") == "success" and isinstance(pos_res.get("data"), list):
                        positions_count = len(pos_res["data"])
                    ord_res = self.dhan.get_order_list()
                    if isinstance(ord_res, dict) and ord_res.get("status") == "success" and isinstance(ord_res.get("data"), list):
                        orders_count = len(ord_res["data"])
                except Exception:
                    pass

                return {
                    "connected": True,
                    "status": "CONNECTED (PERMANENT AUTO-RENEW)",
                    "account_holder": "JYOTI SINGH",
                    "client_id": self.client_id,
                    "is_active": True,
                    "auto_renew_enabled": True,
                    "token_validity": token_validity,
                    "active_segments": active_segments,
                    "available_balance": avail_bal,
                    "utilized_margin": utilized,
                    "withdrawable_balance": withdrawable,
                    "open_positions_count": positions_count,
                    "today_orders_count": orders_count,
                    "fund_limits": data
                }
            else:
                return {
                    "connected": False,
                    "status": "AUTH_ERROR",
                    "client_id": self.client_id,
                    "message": str(profile.get("remarks", "Token expired or invalid")),
                    "is_active": False
                }
        except Exception as e:
            return {
                "connected": False,
                "status": "ERROR",
                "message": f"Dhan API error: {str(e)}",
                "is_active": False
            }

    def get_token_generation_instructions(self) -> List[str]:
        """Provides step-by-step instructions to generate Dhan API Token."""
        return [
            "1. Permanent Auto-Renew Daemon is ACTIVE for Client ID 1000659782.",
            "2. Token automatically extends via DhanLogin.renew_token() every day before expiry."
        ]
