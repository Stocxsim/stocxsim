from flask import Blueprint, request, jsonify, render_template, session
from service.order_service import get_order_details
from service.dashboard_service import weekly_orders_chart, win_rate_chart, profit_loss_chart, top_traded_chart

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

@order_bp.route("/history/weekly-orders-chart")
def generate_weekly_orders_chart():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = weekly_orders_chart(user_id)
    return jsonify({
        "chart": graph_url
    })
    
@order_bp.route("/history/win-rate-chart")
def generate_win_rate_chart():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = win_rate_chart(user_id)
    return jsonify({
        "chart": graph_url
    })


@order_bp.route("/history/profit-loss-chart")
def generate_profit_loss_chart():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = profit_loss_chart(user_id)
    return jsonify({"chart": graph_url})


@order_bp.route("/history/top-traded-chart")
def generate_top_traded_chart():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = top_traded_chart(user_id)
    return jsonify({"chart": graph_url})