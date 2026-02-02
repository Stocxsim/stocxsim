from decimal import Decimal
from service.market_data_service import get_full_market_data
from database.order_dao import insert_order
from database.holding_dao import add_holding, get_holdings_by_user, update_holding_on_sell
from database.userdao import checkBalance, updateBalance

def place_order(user_id, symbol_token, quantity, order_type, price, transaction_type):

    if not user_id:
        raise ValueError("User not logged in")

    quantity = Decimal(quantity)

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    if order_type not in ["market", "limit", "mtf"]:
        raise ValueError("Invalid order type")

    # ✅ MARKET PRICE — convert FLOAT → Decimal
    if order_type == "market":
        ltp = get_full_market_data([symbol_token]).get(
            symbol_token, {}).get("ltp")
        if ltp is None:
            raise ValueError("Could not fetch market price")
        price = Decimal(str(ltp))

    # LIMIT / MTF price
    if order_type in ["mtf"] and (price is None or price <= 0):
        raise ValueError("Price must be greater than zero")

    price = Decimal(price)
    balance = Decimal(str(checkBalance(user_id)))

    # ✅ BALANCE CHECK
    total_cost = price * quantity

    if order_type == "market" or order_type == "limit":
        if transaction_type == "buy" and balance < total_cost:
            raise ValueError("Insufficient balance")

    if order_type == "mtf":
        required = Decimal("0.25") * total_cost
        if transaction_type == "buy" and balance < required:
            raise ValueError("Insufficient balance")
        # MTF only deducts 25% upfront
        price_to_deduct = price * Decimal("0.25")
    else:
        price_to_deduct = price


    if transaction_type not in ["buy", "sell"]:
        raise ValueError("Invalid transaction type")


    holding = get_holdings_by_user(user_id).get(symbol_token)
    if transaction_type == "sell":
        if not holding or Decimal(holding.get("quantity", 0)) < quantity:
            raise ValueError("Insufficient holdings to sell")
        
    # ✅ UPDATE BALANCE
    if transaction_type == "buy":
        new_balance = balance - (quantity * price_to_deduct)
    else:
        new_balance = balance + (quantity * price)

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
        update_holding_on_sell(order_details)

    updateBalance(user_id, new_balance)

    return {
        "message": "Order placed successfully",
        "new_balance": float(new_balance)
    }

