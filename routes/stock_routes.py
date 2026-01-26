from flask import Blueprint, request, jsonify, render_template, session
from database.user_stock_dao import get_stock_tokens_by_user
from service.market_data_service import get_full_market_data
from service.stockservice import search_stocks_service, get_stock_detail_service, rsi_cal
from data.live_data import register_equity_token, LIVE_STOCKS
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
    register_equity_token(str(stock_token))

    stock.set_rsi(rsi_cal(stock_token))
    return render_template("stock.html", stock=stock)


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
