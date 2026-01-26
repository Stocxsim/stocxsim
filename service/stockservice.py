from database.stockdao import search_stocks, get_stock_by_token
from modal.Stock import Stock
from service.market_data_service import fetch_historical_data

import numpy as np

# Service function to search stocks
def search_stocks_service(query):
     rows = search_stocks(query)

     return [
          {
               "token": row[0],
               "name": row[1]
          }
          for row in rows
     ]

# New service function to get stock details by symbol
def get_stock_detail_service(stock_token):
     row = get_stock_by_token(stock_token)

     if not row:
        return None
     
     return Stock(
          stock_token=row[0],
          stock_name=row[1],
     )

def get_closes(token):
    np_result = fetch_historical_data(token)
    return np_result[:, 4].astype(float)


def rsi_cal(closes):
    delta = np.diff(closes)

    gains = np.where(delta > 0, delta, 0)
    losses = np.where(delta < 0, -delta, 0)

    avg_gain = np.mean(gains[-14:])
    avg_loss = np.mean(losses[-14:])

    if avg_loss == 0:
        rsi = 100.0

    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi = round(rsi, 2)

    return rsi

def ema_cal(closes, period):
     
    ema = closes[-1]
    multiplier = 2 / (period + 1)

    for price in reversed(closes[-period:]):
        ema = (price - ema) * multiplier + ema

    return round(ema, 2)