
from flask import Flask, render_template
from extensions import socketio
from routes.user_routes import user_bp
from routes.stock_routes import stock_bp
from routes.trade_routes import trade_bp
from routes.holding_route import holding_bp
from data.live_data import LIVE_STOCKS, LIVE_INDEX

app = Flask(__name__)
app.secret_key = "an12eadf234f"

socketio.init_app(app)
app.register_blueprint(user_bp, url_prefix="/login")
app.register_blueprint(stock_bp, url_prefix="/stocks")
app.register_blueprint(trade_bp, url_prefix="/trade")
app.register_blueprint(holding_bp, url_prefix="/holding")
@app.route("/")
def home():
    return render_template("home.html")

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