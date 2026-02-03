from datetime import datetime, timedelta
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

        # Session TTL is not clearly documented; keep a conservative refresh window.
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


def get_full_market_data(tokens):
    tokens = [str(t) for t in (tokens or []) if t]
    if not tokens:
        return {}

    # Avoid spamming login calls.
    if not _login_if_needed():
        return {}

    try:
        # Most of this app is NSE-only; querying both exchanges increases payload.
        response = _smart.getMarketData(
            mode="FULL",
            exchangeTokens={"NSE": tokens},
        )
        return clean_market_data(response)
    except DataException as ex:
        # Common rate limit response is non-JSON bytes; SmartApi raises DataException.
        msg = str(ex).lower()
        if "exceeding access rate" in msg or "access denied" in msg:
            with _session_lock:
                _blocked_until = time.time() + 60
            print("⚠️ SmartAPI rate limited; backing off for 60s")
            return {}
        raise
    except Exception as ex:
        # If token/session went stale, force relogin once and retry.
        if _login_if_needed(force=True):
            try:
                response = _smart.getMarketData(
                    mode="FULL",
                    exchangeTokens={"NSE": tokens},
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

        cleaned[token] = {
            "prev_close": item.get("close"),
            "ltp": item.get("ltp"),
            "change":item.get("netChange"),
            "percent": item.get("percentChange"),
        }

    return cleaned

def load_baseline_data():
    """
    Load baseline data for index tokens at app startup
    """
    from data.live_data import LIVE_INDEX, BASELINE_DATA, LIVE_STOCKS, INDEX_TOKENS
    
    for token,base in BASELINE_DATA.items():
        data={
            "ltp": base['prev_close'],
            "change": 0,
            "percent_change": 0
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

