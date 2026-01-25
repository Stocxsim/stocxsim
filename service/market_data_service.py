from datetime import datetime,timedelta 
from SmartApi import SmartConnect
import numpy as np
import pyotp
from config import API_KEY, CLIENT_ID, CLIENT_PASSWORD, TOTP_SECRET


def get_full_market_data(tokens):
    

    obj = SmartConnect(api_key=API_KEY)

    totp = pyotp.TOTP(TOTP_SECRET).now()
    session = obj.generateSession(CLIENT_ID, CLIENT_PASSWORD, totp)

    if not session or not session.get("status"):
        raise Exception("Angel One login failed")

    response = obj.getMarketData(mode="FULL", exchangeTokens={
    "NSE": tokens,"BSE": tokens
})
    return clean_market_data(response)

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