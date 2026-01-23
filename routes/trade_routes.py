from decimal import Decimal
from flask import Blueprint, jsonify, request, session
from service.trade_service import place_order
from decimal import Decimal

trade_bp = Blueprint('trade_bp', __name__)


@trade_bp.route("/order", methods=["POST"])
def place_trade_order():
    try:
        user_id = session.get("user_id")
        data = request.form

        symbol_token = data.get("symbol_token")
        quantity = data.get("quantity")
        quantity = int(quantity) if quantity else 0
        order_type = data.get("order_type")
        price = data.get("price")
        price = Decimal(price) if price else None
        transaction_type = data.get("transaction_type")

        result = place_order(
            user_id=user_id,
            symbol_token=symbol_token,
            quantity=quantity,
            order_type=order_type,
            price=price,
            transaction_type=transaction_type
        )

        return jsonify({
            "message": result,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400
