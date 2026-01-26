class Stock:
    def __init__(self, stock_token: int, stock_name: str, rsi: float = None,ema_9: float = None, ema_20: float = None):
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