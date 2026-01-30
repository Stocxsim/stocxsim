from flask import Blueprint, jsonify, session
from service.watchlist_service import toggle_watchlist, is_in_watchlist
from service.stockservice import get_stock_detail_service
from database.watchlist_dao import get_stock_tokens_by_user

watchlist_bp = Blueprint("watchlist", __name__)


# this is stocks/watchlist not login/watchlist
# this is just for the backend api for the javascript to call and get the watchlist data
@watchlist_bp.route("/api")
def api_watchlist():
    user_id = session.get("user_id")
    # print("User ID in session:", user_id)
    if not user_id:
        return jsonify([])   # or return 401

    tokens = [str(t) for t in get_stock_tokens_by_user(user_id)]
    result = []

    for token in tokens:
        stock = get_stock_detail_service(token)

        result.append({
            "token": token,
            "name": stock.stock_name if stock else token,
        })

    return jsonify(result)


# Toggle watchlist status for a stock
@watchlist_bp.route("/toggle/<int:stock_token>", methods=["POST"])
def toggle(stock_token):
#     print("🧪 TOGGLE HIT:", stock_token)
#     print("🧪 SESSION:", dict(session))

     user_id = session.get("user_id")
#     print("🧪 USER ID:", user_id)

     if not user_id:
          return jsonify({"error": "Unauthorized"}), 401

     print("🧪 TOGGLE:")
     status = toggle_watchlist(user_id, stock_token)
     print("🧪 STATUS:", status)
     return jsonify({"watchlisted": status})


# To check watchlist status for a stock
@watchlist_bp.route("/status/<int:stock_token>")
def status(stock_token):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"watchlisted": False})

    status = is_in_watchlist(user_id, stock_token)
    return jsonify({"watchlisted": status})
