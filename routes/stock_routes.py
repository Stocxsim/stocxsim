from flask import Blueprint, request, jsonify, render_template, session
import threading
from database.user_stock_dao import get_stock_tokens_by_user
from service.market_data_service import get_full_market_data
from service.stockservice import search_stocks_service, get_stock_detail_service
from data.live_data import register_equity_token, ensure_baseline_data
from websockets.angle_ws import subscribe_equity_tokens
from database.holding_dao import get_holding_by_user_and_token
from service.indicator_cache import get_cached_indicators, compute_and_cache_indicators
from modal.Stock import Stock

stock_bp = Blueprint("stock_bp", __name__)


@stock_bp.route("/search")
def search_stocks():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    return jsonify(search_stocks_service(query))


@stock_bp.route("/<stock_token>")
def stock_detail(stock_token):
    stock = get_stock_detail_service(stock_token)
    if not stock:
        return render_template("404.html"), 404

    # 🔥 REGISTER TOKEN FOR LIVE UPDATES
    token = str(stock_token)
    register_equity_token(token)
    subscribe_equity_tokens([token])
    threading.Thread(target=ensure_baseline_data, args=([token],), daemon=True).start()

    user_id = session.get("user_id")
    holding = {"quantity": 0, "avg_buy_price": 0}
    if user_id:
        holding = get_holding_by_user_and_token(user_id, stock_token)

    # Indicators are expensive (candle fetch). Use cache + background compute.
    cached = get_cached_indicators(token)
    if cached:
        stock.set_rsi(cached.get("rsi"))
        stock.set_ema_9(cached.get("ema_9"))
        stock.set_ema_20(cached.get("ema_20"))
    else:
        threading.Thread(target=compute_and_cache_indicators, args=(token,), daemon=True).start()
    return render_template("stock.html", stock=stock, holding=holding)


@stock_bp.route("/<stock_token>/indicators")
def stock_indicators(stock_token):
    token = str(stock_token)
    cached = get_cached_indicators(token)
    if cached:
        return jsonify({"status": "ok", "token": token, **cached})

    # Trigger background compute and let client retry.
    threading.Thread(target=compute_and_cache_indicators, args=(token,), daemon=True).start()
    return jsonify({"status": "pending", "token": token})


# this is stocks/watchlist not login/watchlist
# this is just for the backend api for the javascript to call and get the watchlist data
@stock_bp.route("/watchlist")
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
