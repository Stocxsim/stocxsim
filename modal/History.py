"""
modal/History.py
----------------
Data model for storing the closing price of an order at end-of-day.

Used for historical P&L analysis — by recording the closing price at the time
an order was tracked, the system can compute unrealised gains over time.
"""


class History:
    """
    Represents a historical price snapshot tied to an order.

    Attributes:
        history_id  (int)   : Primary key from the history table.
        order_id    (int)   : Foreign key linking to the orders table.
        close_price (float) : End-of-day closing price at the time of recording.
    """
    def __init__(self, history_id: int, order_id: int, close_price: float):
        self.history_id = history_id
        self.order_id = order_id
        self.close_price = close_price

    # -------- Getters --------
    def get_history_id(self):
        return self.history_id

    def get_order_id(self):
        return self.order_id

    def get_close_price(self):
        return self.close_price