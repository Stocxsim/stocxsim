class Stock:
    def __init__(self, stock_token: int, stock_name: str, rsi: float = None):
        self.stock_token = stock_token
        self.stock_name = stock_name
        self.rsi = rsi

    # Getters
    def get_stock_token(self):
        return self.stock_token

    def get_stock_name(self):
        return self.stock_name
    
    def get_rsi(self):
        return self.rsi
    
    # Setters
    def set_stock_token(self, stock_token: int):
        self.stock_token = stock_token
    
    def set_stock_name(self, stock_name: str):
        self.stock_name = stock_name
        
    def set_rsi(self, rsi: float):
        self.rsi = rsi