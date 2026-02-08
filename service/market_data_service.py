from datetime import datetime, timedelta
import os
import sys
import threading
import time

from SmartApi import SmartConnect
from SmartApi.smartExceptions import DataException
import numpy as np
import pyotp

from config import API_KEY, CLIENT_ID, CLIENT_PASSWORD, TOTP_SECRET


# =========================
# SmartAPI session reuse
# =========================

_smart = SmartConnect(api_key=API_KEY)
_session_lock = threading.Lock()
_session_initialized = False
_session_set_at = 0.0
_blocked_until = 0.0


def _login_if_needed(force: bool = False) -> bool:
    """Ensure SmartConnect has a valid session.

    We intentionally reuse a single session to avoid hitting SmartAPI rate limits.
    """
    global _session_initialized, _session_set_at, _blocked_until

    now = time.time()
    if now < _blocked_until:
        return False

    with _session_lock:
        now = time.time()
        if now < _blocked_until:
            return False

        if _session_initialized and not force and (now - _session_set_at) < (30 * 60):
            return True

        totp = pyotp.TOTP(TOTP_SECRET).now()
        session = _smart.generateSession(CLIENT_ID, CLIENT_PASSWORD, totp)

        if not session or not session.get("status"):
            _session_initialized = False
            return False

        _session_initialized = True
        _session_set_at = now
        return True


def get_full_market_data(tokens, exchange: str = "NSE"):
    tokens = [str(t) for t in (tokens or []) if t]
    if not tokens:
        return {}

    if not _login_if_needed():
        return {}

    try:
        response = _smart.getMarketData(
            mode="FULL",
            exchangeTokens={str(exchange).upper(): tokens},
        )
        return clean_market_data(response)
    except DataException as ex:
        msg = str(ex).lower()
        if "exceeding access rate" in msg or "access denied" in msg:
            with _session_lock:
                _blocked_until = time.time() + 60
            print("⚠️ SmartAPI rate limited; backing off for 60s")
            return {}
        raise
    except Exception as ex:
        if _login_if_needed(force=True):
            try:
                response = _smart.getMarketData(
                    mode="FULL",
                    exchangeTokens={str(exchange).upper(): tokens},
                )
                return clean_market_data(response)
            except Exception:
                pass
        raise ex

def clean_market_data(response):
    """
    Angel One FULL API response → UI usable clean data
    """
    
    cleaned = {}

    if not response.get("status"):
        return cleaned

    fetched = response["data"].get("fetched", [])

    for item in fetched:
        token = item["symbolToken"]

        close_val = item.get("close")
        ltp_val = item.get("ltp")
        net_change_val = item.get("netChange")
        pct_val = item.get("percentChange")

        def _to_float(v):
            try:
                return float(v)
            except Exception:
                return None

        close_f = _to_float(close_val)
        ltp_f = _to_float(ltp_val)
        net_change_f = _to_float(net_change_val)
        pct_f = _to_float(pct_val)

        prev_close = close_f
        # Some instruments may not include `close`; derive prev_close when possible.
        if prev_close is None and ltp_f is not None and net_change_f is not None:
            prev_close = ltp_f - net_change_f
        if prev_close is None and ltp_f is not None and pct_f is not None and (1 + (pct_f / 100)) != 0:
            prev_close = ltp_f / (1 + (pct_f / 100))

        cleaned[token] = {
            "prev_close": prev_close,
            "ltp": ltp_f,
            "change": net_change_f,
            "percent": pct_f,
        }
        
    return cleaned


def load_baseline_data():
    """
    Load baseline data for index tokens at app startup
    """
    from data.live_data import LIVE_INDEX, BASELINE_DATA, LIVE_STOCKS, INDEX_TOKENS
    
    for token,base in BASELINE_DATA.items():
        prev_close = base.get("prev_close")
        ltp = base.get("ltp")
        seed_price = ltp if ltp is not None else (prev_close if prev_close is not None else 0)

        change = base.get("change")
        percent = base.get("percent")
        try:
            change_val = float(change) if change is not None else None
        except Exception:
            change_val = None
        try:
            pct_val = float(percent) if percent is not None else None
        except Exception:
            pct_val = None

        # Fallback compute from ltp+prev_close.
        try:
            prev_close_f = float(prev_close) if prev_close is not None else None
        except Exception:
            prev_close_f = None
        try:
            ltp_f = float(seed_price) if seed_price is not None else None
        except Exception:
            ltp_f = None

        if change_val is None and ltp_f is not None and prev_close_f is not None:
            change_val = round(ltp_f - prev_close_f, 2)
        if pct_val is None and ltp_f is not None and prev_close_f not in (None, 0):
            pct_val = round(((ltp_f - prev_close_f) / prev_close_f) * 100, 2)

        if change_val is None:
            change_val = 0.0
        if pct_val is None:
            pct_val = 0.0

        data={
            "ltp": seed_price,
            "change": change_val,
            "percent_change": pct_val
        }
        if token in INDEX_TOKENS:
            LIVE_INDEX[token] = data
        else:
            LIVE_STOCKS[token] = data
    
def fetch_historical_data(symbol_token):
    """
    Fetch historical candle data for a given symbol token and date range.
    """
    obj = SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()
    session = obj.generateSession(CLIENT_ID, CLIENT_PASSWORD, totp)

    if not session or not session.get("status"):
        raise Exception("Angel One login failed")
    # ===== Date Calculation =====
    today = datetime.now()
    from_date = today - timedelta(days=50)

    fromdate_str = from_date.strftime("%Y-%m-%d 09:15")
    todate_str = today.strftime("%Y-%m-%d 15:30")

    # ===== Candle Params =====
    historic_params = {
        "exchange": "NSE",
        "symboltoken": symbol_token,
        "interval": "ONE_DAY",
        "fromdate": fromdate_str,
        "todate": todate_str
    }
    result=obj.getCandleData(historic_params)
    data=result['data']
    np_result = np.array(data)
    return np_result

