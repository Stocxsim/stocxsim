from service.market_data_service import get_full_market_data
LIVE_PRICES = {}
# Preload baseline data for indices
BASELINE_DATA = {}
LIVE_STOCKS = {}
LIVE_INDEX = {}
EQUITY_TOKENS = []  # List of equity stock tokens to track
INDEX_TOKENS = ["26000", "19000", "26009",
                "26013", "53886"]  # List of index tokens to track

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


def refresh_live_data():
    global LIVE_INDEX, LIVE_STOCKS

    # refresh equities (ONLY if registered)
    if EQUITY_TOKENS:
        LIVE_STOCKS = get_full_market_data(tokens=EQUITY_TOKENS)
