class Order:
    def __init__(
        self,
        user_id: int,
        stock_token: int,
        buy_sell: str,
        current_price: float,
        quantity: int
    ):
        self.user_id = user_id
        self.stock_token = stock_token
        self.buy_sell = buy_sell
        self.current_price = current_price
        self.quantity = quantity

    # -------- Getters --------
    def get_user_id(self):
        return self.user_id

    def get_stock_token(self):
        return self.stock_token

    def get_buy_sell(self):
        return self.buy_sell

    def get_current_price(self):
        return self.current_price

    def get_quantity(self):
        return self.quantity