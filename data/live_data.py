from service.market_data_service import get_full_market_data
import threading
from typing import Iterable

LIVE_PRICES={}
BASELINE_DATA={}
LIVE_STOCKS = {}
LIVE_INDEX = {}
EQUITY_TOKENS = []  # List of equity stock tokens to track
INDEX_TOKENS = ["26000","19000","26009","26037","53886"]  # List of index tokens to track

_baseline_lock = threading.Lock()


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
        data={
            "ltp": base['prev_close'],
            "change": 0,
            "percent_change": 0
        }
        if token in INDEX_TOKENS:
            LIVE_INDEX[token] = data
        else:
            LIVE_STOCKS[token] = data

            

def register_equity_token(token: str):
    if token not in EQUITY_TOKENS:
        EQUITY_TOKENS.append(token)
    print("EQUITY_TOKENS:", EQUITY_TOKENS)


def ensure_baseline_data(tokens: Iterable[str]) -> None:
    """Ensure BASELINE_DATA/LIVE_STOCKS have entries for the given tokens.

    This is intentionally safe to call from a request handler, but should ideally
    be run in a background thread because it may hit Angel One's FULL API.
    """
    token_list = [str(t) for t in tokens if t]
    if not token_list:
        return

    with _baseline_lock:
        missing = [t for t in token_list if t not in BASELINE_DATA]
        if not missing:
            return

        fetched = get_full_market_data(tokens=missing)
        if not fetched:
            return

        BASELINE_DATA.update(fetched)

        # Provide an immediate fallback price (prev_close) until websocket ticks arrive.
        for token, base in fetched.items():
            prev_close = base.get("prev_close")
            ltp = base.get("ltp")
            seed_price = ltp if ltp is not None else prev_close
            if seed_price is None:
                seed_price = 0

            data = {
                "ltp": seed_price,
                "change": 0,
                "percent_change": 0,
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
