"""
routes/watchlist_route.py
--------------------------
HTTP endpoints that power the Watchlist feature's DATA API.

IMPORTANT DISTINCTION:
  This blueprint (/watchlist) provides JSON data endpoints called by JavaScript.
  The HTML page rendering for the watchlist is handled by user_routes.py (/login/watchlist).

Blueprint prefix: /watchlist
  GET  /watchlist/api                     → Get all watchlisted stocks with names.
  POST /watchlist/toggle/<stock_token>    → Add or remove a stock from watchlist.
  GET  /watchlist/status/<stock_token>    → Check if a stock is watchlisted.
"""

from flask import Blueprint, jsonify, session
from service.watchlist_service import toggle_watchlist, is_in_watchlist
from service.stockservice import get_stock_detail_service
from database.watchlist_dao import get_stock_tokens_by_user, remove_from_watchlist

from utils.tokens import INDEX_TOKENS

watchlist_bp = Blueprint("watchlist", __name__)


# NOTE: This is the data API for the watchlist page (JavaScript calls this).
# Distinct from /login/watchlist which renders the HTML page itself.
@watchlist_bp.route("/api")
def api_watchlist():
    """
    Return the current user's watchlist as a JSON array.

    Each entry contains: token, stock name, and category.
    Index tokens (NIFTY, SENSEX) are skipped; they live in the top ticker,
    not the watchlist. Any index tokens found are cleaned up from the DB.

    Returns:
      JSON: [list of {token, name, category}] or [] if not logged in.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])

    tokens = get_stock_tokens_by_user(user_id)
    result = []

    for token, category in tokens:
        # Indices (NIFTY/SENSEX/...) are shown in the top ticker, not in Watchlist.
        token_str = str(token)
        if token_str in INDEX_TOKENS:
            # Best-effort cleanup so they don't come back.
            try:
                remove_from_watchlist(user_id, token_str)
            except Exception:
                pass
            continue

        stock = get_stock_detail_service(token)
        result.append({
            "token": token_str,
            "name": stock.stock_name if stock else token,
            "category": category
        })

    return jsonify(result)



# Toggle watchlist status for a stock (add if not in, remove if already in)
@watchlist_bp.route("/toggle/<int:stock_token>", methods=["POST"])
def toggle(stock_token):
    """
    Add a stock to the watchlist if not present, otherwise remove it.

    Returns:
      JSON: {"watchlisted": True|False}
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    status = toggle_watchlist(user_id, stock_token)
    return jsonify({"watchlisted": status})



# Check if a specific stock is currently watchlisted by the user.
@watchlist_bp.route("/status/<int:stock_token>")
def status(stock_token):
    """
    Returns whether the given stock is in the current user's watchlist.

    Returns:
      JSON: {"watchlisted": True|False}
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"watchlisted": False})

    status = is_in_watchlist(user_id, stock_token)
    return jsonify({"watchlisted": status})
