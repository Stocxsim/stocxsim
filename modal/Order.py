"""
modal/Order.py
--------------
Data model representing a single trade order.

Maps closely to the `orders` table schema. The `to_dict()` method serializes
the order to a JSON-safe dict for API responses and the order history page.

order_type values:
  'market' — Full cash order; price fetched at execution time.
  'mtf'    — Margin trade; user pays 25% upfront.

transaction_type values:
  'buy' or 'sell'
"""


class Order:
    """Represents a single simulated trade order."""
    def __init__(
        self,
        order_id: int,
        user_id: int,
        symbol_token: int,
        transaction_type: str,
        price: float,
        quantity: int,
        order_type: str,
        created_at=None
    ):
        self.order_id = order_id
        self.user_id = user_id
        self.symbol_token = symbol_token
        self.transaction_type = transaction_type
        self.price = price
        self.quantity = quantity
        self.order_type = order_type
        self.created_at = created_at

    # -------- Getters --------
    def get_user_id(self):
        return self.user_id

    def get_symbol_token(self):
        return self.symbol_token

    def get_transaction_type(self):
        return self.transaction_type    

    def get_price(self):
        return self.price

    def get_quantity(self):
        return self.quantity
    
    def get_order_type(self):
        return self.order_type
    
    def get_created_at(self):
        return self.created_at
    
    def get_order_id(self):
        return self.order_id



    # -------- JSON Serializer --------
    def to_dict(self):
        """
        Serialize the Order to a JSON-safe dict.

        Note: symbol_token is kept as a string here; callers should map it
        to a stock name using `get_stock_by_token()` if needed.
        """
        return {
            "order_id": self.order_id,
            "symbol": str(self.symbol_token),  # Map token -> name at the caller level
            "transaction_type": self.transaction_type,
            "price": float(self.price),
            "quantity": int(self.quantity),
            "order_type": self.order_type,
            "product": "REGULAR",
            "time": (
                self.created_at.strftime("%I:%M %p")
                if self.created_at else ""
            )
        }