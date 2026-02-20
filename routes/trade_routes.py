"""
routes/trade_routes.py
----------------------
HTTP endpoints for executing simulated buy/sell trades.

All trade logic (price validation, tax calculations, balance updates, etc.)
is delegated to `service/trade_service.py`.

Blueprint prefix: /trade
  POST /trade/order  → place a new order
"""

from decimal import Decimal
from flask import Blueprint, jsonify, request, session
from service.trade_service import place_order
from decimal import Decimal

trade_bp = Blueprint('trade_bp', __name__)



@trade_bp.route("/order", methods=["POST"])
def place_trade_order():
    """
    Place a simulated buy or sell order.

    Expected form fields:
      - symbol_token    (str)  : Angel One token for the selected stock.
      - quantity        (str)  : Number of shares.
      - order_type      (str)  : 'market' (full cash) or 'mtf' (25% margin).
      - price           (str)  : Required only for MTF orders (limit price).
      - transaction_type(str)  : 'buy' or 'sell'.

    Returns:
      JSON with 'message', 'new_balance', and 'charges' on success;
      JSON with 'error' on failure.
    """
    try:
        # Verify the user is logged in before processing any order.
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Please login first"}), 401

        data = request.form
        symbol_token = data.get("symbol_token")

        # Convert quantity to Decimal for precise monetary calculations.
        quantity = data.get("quantity")
        quantity = Decimal(quantity) if quantity else Decimal("0")

        order_type = data.get("order_type")  # 'market' or 'mtf'

        # Price is only required for MTF orders; market orders use live LTP.
        price = data.get("price")
        price = Decimal(price) if price else None

        transaction_type = data.get("transaction_type")  # 'buy' or 'sell'

        result = place_order(
            user_id=user_id,
            symbol_token=symbol_token,
            quantity=quantity,
            order_type=order_type,
            price=price,
            transaction_type=transaction_type
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 400
