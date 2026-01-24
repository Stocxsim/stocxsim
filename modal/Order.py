class Order:
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
