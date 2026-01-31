from database.order_dao import get_order
from service.stockservice import get_stock_detail_service

def get_order_details(user_id, filter_params):
    """
    Fetches orders from DB, enriches them with stock name, and returns a list of dicts
    ready for frontend consumption.
    """
    stack = get_order(user_id, filter_params)
    orders_list = []

    while not stack.is_empty():
        order = stack.pop()

        # Fetch stock details by symbol_token
        stock = get_stock_detail_service(order.get_symbol_token())
        stock_name = stock.stock_name if stock else "Unknown"

        orders_list.append({
            "order_id": order.get_order_id(),
            "symbol_token": order.get_symbol_token(),
            "symbol": stock_name,  # <-- this is what your JS will display
            "transaction_type": order.get_transaction_type(),
            "quantity": order.get_quantity(),
            "price": order.get_price(),
            "order_type": order.get_order_type(),
            "time": order.get_created_at().strftime("%I:%M %p"),
            "date": order.get_created_at().strftime("%d %b %Y")
        })

    return orders_list