"""
routes/order_route.py
---------------------
HTTP endpoints for order history retrieval and analytics chart generation.

Blueprint prefix: /order
  GET|POST /order/history                     → Fetch user's order history.
  GET      /order/history/weekly-orders-chart → Plotly HTML: orders per week.
  GET      /order/history/win-rate-chart      → Plotly HTML: win/loss pie.
  GET      /order/history/profit-loss-chart   → Plotly HTML: profit vs loss.
  GET      /order/history/top-traded-chart    → Plotly HTML: top 5 traded.
  GET      /order/search?q=QUERY              → Search orders by stock name.

Charts are rendered server-side using Plotly and returned as HTML fragments
that are injected into the dashboard page by the frontend JavaScript.
"""

from flask import Blueprint, request, jsonify, render_template, session
from service.order_service import get_order_details, search_orders_service
from service.dashboard_service import weekly_orders_chart, win_rate_chart, profit_loss_chart, top_traded_chart


order_bp = Blueprint('order_bp', __name__)



@order_bp.route("/history", methods=["GET", "POST"])
def order_history():
    """
    Fetch the logged-in user's trade order history.

    Accepts optional POST body with filter_params dict to narrow results
    (e.g., filter by date range, stock, transaction type).

    Returns:
      JSON: {"orders": [list of order dicts]}
    """
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
    """Return a Plotly bar chart (HTML fragment) of weekly order counts."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = weekly_orders_chart(user_id)
    return jsonify({
        "chart": graph_url
    })



@order_bp.route("/history/win-rate-chart")
def generate_win_rate_chart():
    """Return a Plotly donut chart (HTML fragment) showing win-vs-loss percentage."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = win_rate_chart(user_id)
    return jsonify({
        "chart": graph_url
    })



@order_bp.route("/history/profit-loss-chart")
def generate_profit_loss_chart():
    """Return a Plotly bar chart (HTML fragment) with total simulated profit vs loss."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = profit_loss_chart(user_id)
    return jsonify({"chart": graph_url})



@order_bp.route("/history/top-traded-chart")
def generate_top_traded_chart():
    """Return a Plotly bar chart (HTML fragment) showing the top 5 most-traded stocks."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    graph_url = top_traded_chart(user_id)
    return jsonify({"chart": graph_url})



# for order page search filter
@order_bp.route("/search")
def search_orders():
    """
    Search orders by stock name/symbol for the Orders page filter bar.

    Query params:
      q (str): Partial stock name to match (case-insensitive).

    Returns:
      JSON: list of matching order dicts or [] if no query given.
    """
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