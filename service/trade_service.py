from decimal import Decimal
from service.market_data_service import get_full_market_data
from database.order_dao import insert_order
from database.holding_dao import add_holding, get_holdings_by_user, update_holding_on_sell
from database.userdao import checkBalance, updateBalance
from database.transaction_dao import insert_transaction
from database.stockdao import get_stock_by_token

def place_order(user_id, symbol_token, quantity, order_type, price, transaction_type):
    if not user_id:
        raise ValueError("User not logged in")

    quantity = Decimal(quantity)

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero")

    if order_type not in ["market", "mtf"]:
        raise ValueError("Invalid order type")

    if order_type == "market":
        ltp = get_full_market_data([symbol_token]).get(
            symbol_token, {}).get("ltp")
        if ltp is None:
            raise ValueError("Could not fetch market price")
        price = Decimal(str(ltp))

    # MTF price
    if order_type in ["mtf"] and (price is None or price <= 0):
        raise ValueError("Price must be greater than zero")

    price = Decimal(price)
    balance = Decimal(str(checkBalance(user_id)))

    # ✅ BALANCE CHECK
    total_cost = price * quantity

    if order_type == "market" :
        if transaction_type == "buy" and balance < total_cost:
            raise ValueError("Insufficient balance")
        
    # `get_holdings_by_user` returns a dict keyed by token string; iterating it yields keys (strings),
    # so we must iterate over `.values()` to access holding dicts.
    holdings = get_holdings_by_user(user_id)
    holding = next(
        (
            h for h in holdings.values()
            if str(h.get('symbol_token')) == str(symbol_token)
            and str(h.get('order_type')) == str(order_type)
        ),
        None
    )

    if transaction_type == "sell":
        if not holding or Decimal(str(holding.get("quantity", 0))) < quantity:
            raise ValueError("Insufficient holdings to sell")

    if transaction_type not in ["buy", "sell"]:
        raise ValueError("Invalid transaction type")

    if order_type == "mtf":
        if transaction_type == "buy":
            required = Decimal("0.25") * total_cost
            if balance < required:
                raise ValueError("Insufficient balance")
            # MTF only deducts 25% upfront
            cash_flow = -(required)
        elif transaction_type == "sell":
            loan_amount = holding.get("avg_buy_price")*quantity*Decimal("0.75")
            cash_flow= total_cost - loan_amount
    else:
        # Standard Market Order (100% Cash)
        if transaction_type == "buy":
            if balance < total_cost:
                raise ValueError("Insufficient balance")
            cash_flow = -total_cost
        else: # Market Sell
            cash_flow = total_cost
    
    if transaction_type == "sell":
        if not holding or Decimal(holding.get("quantity", 0)) < quantity:
            raise ValueError("Insufficient holdings to sell")
        
    # ✅ UPDATE BALANCE
    if transaction_type == "buy":
        new_balance = balance + cash_flow
    else:
        new_balance = balance + cash_flow


        
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

    transaction_amt = abs(cash_flow)

    updateBalance(user_id, new_balance)
    insert_transaction(user_id, transaction_amt, transaction_type.upper(), get_stock_by_token(symbol_token)[1])

    return {
        "message": "Order placed successfully",
        "new_balance": float(new_balance)
    }

