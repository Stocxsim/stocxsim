from database.userdao import checkBalance
from service.market_data_service import get_full_market_data
from database.order_dao import insert_order
from database.holding_dao import add_holding,get_holdings_by_user, update_holding_on_sell


def place_order(user_id, symbol_token, quantity, order_type, price, transaction_type):
    # Placeholder implementation for placing a buy order
    if not user_id:
        raise ValueError("User not logged in")

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    if order_type not in ["market", "limit","mtf"]:
        raise ValueError("Invalid order type")

    if order_type=="market":
        price = get_full_market_data([symbol_token]).get(symbol_token, {}).get("ltp")
        if price is None:
            raise ValueError("Could not fetch market price for the symbol token")

    if order_type in [ "mtf"] and (price is None or price <= 0):
        raise ValueError("Price must be greater than zero for limit orders")
    
    if (order_type in ["market"] and checkBalance(user_id) < price * quantity) or (order_type=="mtf" and checkBalance(user_id) < (0.25*price*quantity)):
        raise ValueError("Insufficient balance")
    
    if order_type=="mtf":
        price = price * 0.25

    if transaction_type not in ["buy", "sell"]:
        raise ValueError("Invalid transaction type")

    holding = get_holdings_by_user(user_id).get(symbol_token)

    if transaction_type == "sell":
        if not holding or holding.get("quantity", 0) < quantity:
            raise ValueError("Insufficient holdings to sell")

    
    # Simulate order placement logic
    order_details = {
        "user_id": user_id,
        "symbol_token": symbol_token,
        "quantity": quantity,
        "order_type": order_type,
        "price": price,
        "transaction_type": transaction_type
    }
    insert_order(order_details)
    if transaction_type == "buy":
        add_holding(order_details)
    else:
        if not update_holding_on_sell(order_details):
            return "Sell order failed: insufficient holdings"
    return "Order placed successfully"