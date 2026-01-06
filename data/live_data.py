from service.market_data_service import get_full_market_data
LIVE_PRICES={}
BASELINE_DATA=get_full_market_data(tokens=["99926000","99919000","99926009","99926013","53886"])  # Preload baseline data for indices
LIVE_STOCKS = {}
LIVE_INDEX = {}