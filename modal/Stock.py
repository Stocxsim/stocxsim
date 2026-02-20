"""
modal/Stock.py
--------------
Data model representing a stock instrument with optional technical indicators.

The Stock object is built from data queried from the `stocks` table and
enriched with RSI/EMA values computed by the stockservice.
"""


class Stock:
    """
    Represents a stock's identity and optionally its technical indicator values.

    Attributes:
        stock_token (int)   : Angel One instrument token (unique identifier).
        stock_name  (str)   : Human-readable name (e.g., "RELIANCE").
        rsi         (float) : 14-period RSI; None if not yet calculated.
        ema_9       (float) : 9-period EMA;  None if not yet calculated.
        ema_20      (float) : 20-period EMA; None if not yet calculated.
    """
    def __init__(self, stock_token: int, stock_name: str, rsi: float = None, ema_9: float = None, ema_20: float = None):
        self.stock_token = stock_token
        self.stock_name = stock_name
        self.rsi = rsi
        self.ema_9 = ema_9
        self.ema_20 = ema_20

    # Getters
    def get_stock_token(self):
        return self.stock_token

    def get_stock_name(self):
        return self.stock_name
    
    def get_rsi(self):
        return self.rsi
    
    def get_ema_9(self):
        return self.ema_9
    
    def get_ema_20(self):
        return self.ema_20
    
    # Setters
    def set_stock_token(self, stock_token: int):
        self.stock_token = stock_token
    
    def set_stock_name(self, stock_name: str):
        self.stock_name = stock_name
        
    def set_rsi(self, rsi: float):
        self.rsi = rsi

    def set_ema_9(self, ema_9: float):
        self.ema_9 = ema_9

    def set_ema_20(self, ema_20: float):
        self.ema_20 = ema_20