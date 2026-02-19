from flask import Blueprint, request, jsonify, render_template, session
from websockets.angle_ws import subscribe, unsubscribe, subscribe_equity_tokens
from websockets import angle_ws
from service.stockservice import search_stocks_service, get_stock_detail_service
from data.live_data import register_equity_token, ensure_baseline_data, LIVE_INDEX, INDEX_TOKENS, BASELINE_DATA
from data.live_data import load_baseline_data
from database.holding_dao import get_holding_by_user_and_token
from service.indicator_cache import get_cached_indicators, compute_and_cache_indicators

import threading

stock_bp = Blueprint("stock_bp", __name__)


@stock_bp.route("/index/snapshot")
def index_snapshot():
    """Fallback snapshot for index ticker (NIFTY/SENSEX/...)."""
    try:
        ensure_baseline_data(INDEX_TOKENS)
        if not LIVE_INDEX:
            load_baseline_data()

        # Ensure all index tokens have an entry
        for t in INDEX_TOKENS:
            t = str(t)
            if t not in LIVE_INDEX:
                base = BASELINE_DATA.get(t) or {}
                prev_close = base.get("prev_close")
                ltp = base.get("ltp")
                seed = ltp if ltp is not None else (
                    prev_close if prev_close is not None else 0)

                change = base.get("change")
                percent = base.get("percent")
                try:
                    change_val = float(change) if change is not None else None
                except Exception:
                    change_val = None
                try:
                    pct_val = float(percent) if percent is not None else None
                except Exception:
                    pct_val = None

                # Compute from seed+prev_close if needed.
                try:
                    prev_close_f = float(
                        prev_close) if prev_close is not None else None
                except Exception:
                    prev_close_f = None
                try:
                    ltp_f = float(seed) if seed is not None else None
                except Exception:
                    ltp_f = None

                if change_val is None and ltp_f is not None and prev_close_f is not None:
                    change_val = round(ltp_f - prev_close_f, 2)
                if pct_val is None and ltp_f is not None and prev_close_f not in (None, 0):
                    pct_val = round(
                        ((ltp_f - prev_close_f) / prev_close_f) * 100, 2)

                if change_val is None:
                    change_val = 0.0
                if pct_val is None:
                    pct_val = 0.0

                LIVE_INDEX[t] = {
                    "ltp": seed, "change": change_val, "percent_change": pct_val}

        return jsonify({"index": LIVE_INDEX})
    except Exception as e:
        return jsonify({"error": str(e), "index": LIVE_INDEX}), 200


# for subscribing and unsubscribing stocks for live data (Specially for search)
@stock_bp.route("/subscribe/<token>", methods=["POST"])
def subscribe_stock(token):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    try:

        register_equity_token(token)
        try:
            ensure_baseline_data([token])
        except Exception as e:
            print("⚠️ BASELINE DATA ERROR:", e)

        if angle_ws.ws is None:
            return jsonify({"error": "WS not connected"}), 500

        subscribe(angle_ws.ws, 1, str(token))
        return jsonify({"status": "subscribed", "token": token})
    except Exception as e:
        print("❌ SUBSCRIBE ERROR:", e)
        return jsonify({"error": str(e)}), 500


@stock_bp.route("/unsubscribe/<token>", methods=["POST"])
def unsubscribe_stock(token):
    try:
        if angle_ws.ws is None:
            return jsonify({"error": "WS not connected"}), 500

        unsubscribe(angle_ws.ws, 1, str(token))

        return jsonify({"status": "unsubscribed", "token": token})

    except Exception as e:
        print("❌ UNSUBSCRIBE ERROR:", e)
        return jsonify({"error": str(e)}), 500


# routes for stock details and search
@stock_bp.route("/search")
def search_stocks():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify([])

    return jsonify(search_stocks_service(query))


# Searched stock action route.
@stock_bp.route("/<stock_token>")
def stock_detail(stock_token):
    stock = get_stock_detail_service(stock_token)
    if not stock:
        return render_template("404.html"), 404
    # 🔥 REGISTER TOKEN FOR LIVE UPDATES
    token = str(stock_token)
    register_equity_token(token)
    subscribe_equity_tokens([token])
    threading.Thread(target=ensure_baseline_data,
                     args=([token],), daemon=True).start()

    user_id = session.get("user_id")
    holding = {"market": {"quantity": 0, "avg_buy_price": 0},
               "mtf": {"quantity": 0, "avg_buy_price": 0}}
    if user_id:
        holding = get_holding_by_user_and_token(user_id, stock_token) or holding

    cached = get_cached_indicators(token)
    if cached:
        stock.set_rsi(cached.get("rsi"))
        stock.set_ema_9(cached.get("ema_9"))
        stock.set_ema_20(cached.get("ema_20"))
    else:
        threading.Thread(target=compute_and_cache_indicators,
                         args=(token,), daemon=True).start()
    return render_template("stock.html", stock=stock, holdings=holding)


@stock_bp.route("/<stock_token>/indicators")
def stock_indicators(stock_token):
    token = str(stock_token)
    cached = get_cached_indicators(token)
    if cached:
        return jsonify({"status": "ok", "token": token, **cached})

    threading.Thread(target=compute_and_cache_indicators,
                     args=(token,), daemon=True).start()
    return jsonify({"status": "pending", "token": token})