from decimal import Decimal
from service.market_data_service import get_full_market_data
from database.order_dao import insert_order
from database.holding_dao import add_holding, get_holdings_by_user, update_holding_on_sell
from database.userdao import checkBalance, updateBalance
from database.transaction_dao import insert_transaction
from database.stockdao import get_stock_by_token


BUY_TAX_RATE = Decimal("0.000190356")
SELL_TAX_RATE = Decimal("0.001039")
FIXED_DP_CHARGE = Decimal("15.93")


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
    gross_trade_value = price * quantity

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

# Default order charges to zero; will be calculated based on order type and transaction type
    order_charges = Decimal("0")

    if order_type == "mtf":
        if transaction_type == "buy":
            required = Decimal("0.25") * gross_trade_value
            if balance < required:
                raise ValueError("Insufficient balance")
            # MTF only deducts 25% upfront
            cash_flow = -(required)
        elif transaction_type == "sell":

            # TAX/Fees calculation :-  Delayed tax calculation for MTF Sell
            avg_buy_price = Decimal(str(holding.get("avg_buy_price")))
            delayed_buy_tax = (avg_buy_price * quantity) * BUY_TAX_RATE
            current_sell_tax = (gross_trade_value *
                                SELL_TAX_RATE) + FIXED_DP_CHARGE
            order_charges = delayed_buy_tax + current_sell_tax

            loan_amount = holding.get("avg_buy_price")*quantity*Decimal("0.75")
            cash_flow = gross_trade_value - loan_amount - order_charges
    else:
        # Standard Market Order (100% Cash)
        if transaction_type == "buy":
            if balance < gross_trade_value:
                raise ValueError("Insufficient balance")
            cash_flow = -gross_trade_value
        else:  # Market Sell
            # TAX/Fees calculation for Market Sell
            avg_buy_price = Decimal(str(holding.get("avg_buy_price")))
            delayed_buy_tax = (avg_buy_price * quantity) * BUY_TAX_RATE
            current_sell_tax = (gross_trade_value *
                                SELL_TAX_RATE) + FIXED_DP_CHARGE
            order_charges = delayed_buy_tax + current_sell_tax

            cash_flow = gross_trade_value - order_charges

    # ✅ UPDATE BALANCE
    new_balance = balance + cash_flow

    order_details = {
        "user_id": user_id,
        "symbol_token": symbol_token,
        "quantity": quantity,
        "order_type": order_type,
        "price": price,
        "transaction_type": transaction_type,
        "charges": float(order_charges)
    }

    insert_order(order_details)

    if transaction_type == "buy":
        add_holding(order_details)
    else:
        update_holding_on_sell(order_details)

    transaction_amt = abs(cash_flow)

    updateBalance(user_id, new_balance)
    insert_transaction(user_id, transaction_amt, transaction_type.upper(
    ), get_stock_by_token(symbol_token)[1])

    return {
        "message": "Order placed successfully",
        "new_balance": round(float(new_balance), 2),
        "charges": float(order_charges)
    }
