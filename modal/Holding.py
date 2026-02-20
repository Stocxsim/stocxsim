"""
modal/Holding.py
----------------
Data model representing a user's current position in a single stock.

Note: `last_close` is used to compute unrealised P&L on the portfolio page
(unrealised_pnl = (current_ltp - avg_buy_price) * quantity).
"""


class Holding:
    """
    Represents one row in a user's portfolio.

    Attributes:
        stock_token (int)   : Angel One instrument token.
        last_close  (float) : Previous day's closing price (for % change calc).
        price       (float) : Average buy price across all lots.
    """
    def __init__(self, stock_token: int, last_close: float, price: float):
        self.stock_token = stock_token
        self.last_close = last_close
        self.price = price

    # -------- Getters --------
    def get_stock_token(self):
        return self.stock_token

    def get_last_close(self):
        return self.last_close

    def get_price(self):
        return self.price