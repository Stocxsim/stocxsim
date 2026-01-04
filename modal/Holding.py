class Holding:
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