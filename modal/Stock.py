class Stock:
    def __init__(self, stock_token: int, stock_name: str):
        self.stock_token = stock_token
        self.stock_name = stock_name

    # Getters
    def get_stock_token(self):
        return self.stock_token

    def get_stock_name(self):
        return self.stock_name