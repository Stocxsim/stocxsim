from service.market_data_service import get_full_market_data
import threading
import time
from typing import Iterable

from utils.tokens import NSE_INDEX_TOKENS, BSE_INDEX_TOKENS, INDEX_TOKENS

LIVE_PRICES={}
BASELINE_DATA={}
LIVE_STOCKS = {}
LIVE_INDEX = {}
EQUITY_TOKENS = []  # List of equity stock tokens to track


_baseline_lock = threading.Lock()
_baseline_in_flight = set()
_baseline_retry_after = 0.0


# def refresh_live_data():
#     global LIVE_INDEX, LIVE_STOCKS

#     # index live data
#     LIVE_INDEX = get_full_market_data(tokens=INDEX_TOKENS)

#     # equity live data (if any)
#     if EQUITY_TOKENS:
#         LIVE_STOCKS = get_full_market_data(tokens=EQUITY_TOKENS)


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

        # If SmartAPI didn't provide netChange/percentChange, compute from ltp+prev_close.
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

            

def register_equity_token(token: str):
    if token not in EQUITY_TOKENS:
        EQUITY_TOKENS.append(token)


def ensure_baseline_data(tokens: Iterable[str]) -> None:
    """Ensure BASELINE_DATA/LIVE_STOCKS have entries for the given tokens.

    This is intentionally safe to call from a request handler, but should ideally
    be run in a background thread because it may hit Angel One's FULL API.
    """
    token_list = [str(t) for t in tokens if t]
    if not token_list:
        return

    global _baseline_retry_after
    now = time.time()
    if now < _baseline_retry_after:
        return

    # Decide what to fetch under lock; do network call outside lock.
    with _baseline_lock:
        missing = [t for t in token_list if t not in BASELINE_DATA and t not in _baseline_in_flight]
        if not missing:
            return
        for t in missing:
            _baseline_in_flight.add(t)

    try:
        # Fetch NSE vs BSE separately (Sensex requires BSE).
        missing_nse = [t for t in missing if t not in BSE_INDEX_TOKENS]
        missing_bse = [t for t in missing if t in BSE_INDEX_TOKENS]

        fetched = {}
        if missing_nse:
            fetched.update(get_full_market_data(tokens=missing_nse, exchange="NSE"))
        if missing_bse:
            fetched.update(get_full_market_data(tokens=missing_bse, exchange="BSE"))
            

    except Exception as e:
        # Never crash the caller thread; just retry later.
        print(f"⚠️ Baseline fetch error: {e}")
        fetched = {}

    with _baseline_lock:
        for t in missing:
            _baseline_in_flight.discard(t)

        if not fetched:
            # Most common cause is SmartAPI rate limit; wait a bit before retry.
            _baseline_retry_after = time.time() + 60
            return

        BASELINE_DATA.update(fetched)

        # Provide an immediate fallback price (prev_close) until websocket ticks arrive.
        for token, base in fetched.items():
            prev_close = base.get("prev_close")
            ltp = base.get("ltp")
            seed_price = ltp if ltp is not None else prev_close
            if seed_price is None:
                seed_price = 0

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

            # If SmartAPI didn't provide netChange/percentChange, compute from ltp+prev_close.
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

            data = {
                "ltp": seed_price,
                "change": change_val,
                "percent_change": pct_val,
            }

            if token in INDEX_TOKENS:
                LIVE_INDEX[token] = data
            else:
                LIVE_STOCKS[token] = data


def refresh_live_data():
    global LIVE_INDEX, LIVE_STOCKS

    # refresh equities (ONLY if registered)
    if EQUITY_TOKENS:
        LIVE_STOCKS = get_full_market_data(tokens=EQUITY_TOKENS)
