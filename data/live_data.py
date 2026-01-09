from service.market_data_service import get_full_market_data
LIVE_PRICES={}
BASELINE_DATA={}
LIVE_STOCKS = {}
LIVE_INDEX = {}
EQUITY_TOKENS = []  # List of equity stock tokens to track
INDEX_TOKENS = ["26000","19000","26009","26013","53886"]  # List of index tokens to track

# def refresh_live_data():
#     global LIVE_INDEX, LIVE_STOCKS

#     # index live data
#     LIVE_INDEX = get_full_market_data(tokens=INDEX_TOKENS)

#     # equity live data (if any)
#     if EQUITY_TOKENS:
#         LIVE_STOCKS = get_full_market_data(tokens=EQUITY_TOKENS)