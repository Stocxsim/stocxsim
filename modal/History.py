class History:
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