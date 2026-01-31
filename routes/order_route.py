from flask import Blueprint, request, jsonify, render_template, session
from service.order_service import get_order_details

order_bp = Blueprint('order_bp', __name__)


@order_bp.route("/history", methods=["POST"])
def order_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    filter_params = request.json.get("filter_params", {})
    try:
        orders = get_order_details(user_id, filter_params)
        return jsonify({
            "orders": orders
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400
