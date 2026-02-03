
from flask import Flask, render_template, jsonify
from extensions import socketio
from routes.user_routes import user_bp
from routes.stock_routes import stock_bp
from routes.trade_routes import trade_bp
from routes.holding_route import holding_bp
from routes.watchlist_route import watchlist_bp
from routes.order_route import order_bp
from routes.profile_route import profile_bp
from routes.transaction_route import transaction_bp

from data.live_data import LIVE_STOCKS, LIVE_INDEX

app = Flask(__name__)
app.secret_key = "an12eadf234f"

socketio.init_app(app)
app.register_blueprint(user_bp, url_prefix="/login")
app.register_blueprint(stock_bp, url_prefix="/stocks")
app.register_blueprint(trade_bp, url_prefix="/trade")
app.register_blueprint(holding_bp, url_prefix="/holding")
app.register_blueprint(transaction_bp, url_prefix="/transactions")
app.register_blueprint(watchlist_bp, url_prefix="/watchlist")
app.register_blueprint(order_bp, url_prefix="/order")
app.register_blueprint(profile_bp, url_prefix="/profile")

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/debug/routes")
def debug_routes():
    """Development helper: list registered routes (useful when diagnosing 404s after code changes)."""
    routes = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"})
        routes.append({"rule": rule.rule, "endpoint": rule.endpoint, "methods": methods})
    return jsonify({"routes": routes})

@socketio.on("connect")
def on_connect():
    print("🟢 Client connected")

    # 🔥 Send data immediately on connect
    # if is_market_open():
    socketio.emit("live_prices", {
        "stocks": LIVE_STOCKS,
        "index": LIVE_INDEX
    })
    # else:
    #     socketio.emit("live_prices", {
            
    #         "index": BASELINE_DATA
    #     })