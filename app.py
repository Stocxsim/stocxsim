# from flask import Flask, render_template,session

# from routes.user_routes import user_bp
# from flask_socketio import SocketIO

# app = Flask(__name__)
# app.secret_key = "an12eadf234f" 
# # Socket.IO register
# socketio = SocketIO(
#     app,
#     cors_allowed_origins="*",   # frontend alag port hoy to bhi chale
#     async_mode="threading"       # IMPORTANT
# )


# app.register_blueprint(user_bp, url_prefix='/login')

# @app.route("/")
# def home():
#     return render_template("home.html")

# app.py
from flask import Flask, render_template
from flask_socketio import SocketIO
from routes.user_routes import user_bp
from data.live_data import LIVE_STOCKS, LIVE_INDEX,BASELINE_DATA
    
from utils.market_time import is_market_open

app = Flask(__name__)
app.secret_key = "an12eadf234f"

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

app.register_blueprint(user_bp, url_prefix="/login")

@app.route("/")
def home():
    return render_template("home.html")

@socketio.on("connect")
def on_connect():
    print("🟢 Client connected")

    # 🔥 Send data immediately on connect
    if is_market_open():
        socketio.emit("live_prices", {
            "stocks": LIVE_STOCKS,
            "index": LIVE_INDEX
        })
    else:
        socketio.emit("live_prices", {
            
            "index": BASELINE_DATA
        })