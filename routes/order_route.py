from flask import Blueprint, request, jsonify, render_template, session
from service.order_service import get_order_details, search_orders_service
from service.dashboard_service import weekly_orders_chart, win_rate_chart, profit_loss_chart, top_traded_chart


order_bp = Blueprint('order_bp', __name__)


@order_bp.route("/history", methods=["GET", "POST"])
def order_history():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            filter_params = data.get("filter_params", {})
        else:
            filter_params = {}
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


# for order page search filter
@order_bp.route("/search")
def search_orders():
    query = request.args.get("q", "").strip()
    print(f"Search Query: '{query}'")  # Debug log
    if not query:
        return jsonify([])

    try:
        results = search_orders_service(query)
        return jsonify(results)
    except Exception as e:
        print(f"Search Error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500