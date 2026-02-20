"""
service/stockservice.py
-----------------------
Service layer for stock search, stock details, and technical indicator calculations.

Technical Indicators:
  - RSI (Relative Strength Index): Momentum indicator.
    Values above 70 = overbought; below 30 = oversold.
  - EMA (Exponential Moving Average): Trend-following indicator.
    Uses exponential weighting of recent prices.
    EMA-9 and EMA-20 are commonly used crossover signals.

Historical data (last 50 days, daily candles) is fetched from Angel One
SmartAPI and processed as a NumPy array for performance.
"""

from database.stockdao import search_stocks, get_stock_by_token
from modal.Stock import Stock
from service.market_data_service import fetch_historical_data

import numpy as np


# Service function to search stocks by name/symbol (used by the search bar)
def search_stocks_service(query):
    """
    Full-text search for stocks matching the query string.

    Args:
        query (str): Partial stock name or symbol entered by the user.

    Returns:
        list of dicts: [{token, name, symbol, exchange}, ...]
    """
    rows = search_stocks(query)

    return [
         {
              "token": row[0],
              "name": row[1],
              "symbol": row[2],
              "exchange": row[3]
         }
         for row in rows
    ]


# Service function to get full stock details by Angel One token
def get_stock_detail_service(stock_token):
    """
    Fetch a single stock's details and return a Stock model object.

    Args:
        stock_token (str|int): Angel One instrument token.

    Returns:
        Stock object or None if not found in the database.
    """
    row = get_stock_by_token(stock_token)

    if not row:
       return None

    return Stock(
         stock_token=row[0],
         stock_name=row[1],
    )


def get_closes(token):
    """
    Fetch the last 50 days of daily closing prices for a given stock token.

    Returns:
        numpy.ndarray: 1D array of float closing prices.
    """
    np_result = fetch_historical_data(token)
    return np_result[:, 4].astype(float)  # Column index 4 is the close price



def rsi_cal(closes):
    """
    Calculate the 14-period Relative Strength Index (RSI).

    RSI = 100 - 100 / (1 + RS)
    RS  = Average Gain over 14 periods / Average Loss over 14 periods

    Args:
        closes (numpy.ndarray): Array of closing prices.

    Returns:
        float: RSI value rounded to 2 decimal places.
    """
    delta = np.diff(closes)  # Day-to-day price changes

    gains = np.where(delta > 0, delta, 0)    # Positive movements
    losses = np.where(delta < 0, -delta, 0)  # Absolute negative movements

    avg_gain = np.mean(gains[-14:])   # Average of the last 14 gains
    avg_loss = np.mean(losses[-14:])  # Average of the last 14 losses

    if avg_loss == 0:
        rsi = 100.0  # No losses in the period = maximum strength
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        rsi = round(rsi, 2)

    return rsi


def ema_cal(closes, period):
    """
    Calculate the Exponential Moving Average (EMA) for a given period.

    Uses a smoothing multiplier: k = 2 / (period + 1)
    Each new EMA = (Price - Previous EMA) * k + Previous EMA

    Args:
        closes (numpy.ndarray): Array of closing prices.
        period (int)          : Number of periods (e.g., 9 for EMA-9).

    Returns:
        float: EMA value rounded to 2 decimal places.
    """
    ema = closes[-1]  # Seed EMA with the most recent closing price
    multiplier = 2 / (period + 1)

    # Iterate backward through the last `period` closes to apply weighting.
    for price in reversed(closes[-period:]):
        ema = (price - ema) * multiplier + ema

    return round(ema, 2)