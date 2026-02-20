"""
app.py
------
Flask application factory for Stocxsim.

Responsibilities:
  - Create and configure the Flask app object.
  - Register all feature Blueprints with their URL prefixes.
  - Attach the SocketIO server (from extensions.py).
  - Define top-level routes (home, debug).
  - Register the Socket.IO 'connect' event handler which seeds live data.
"""

from datetime import timedelta

from flask import Flask, render_template, jsonify, session, redirect
from extensions import socketio

# --- Blueprint imports (each feature owns its own routes file) ---
from routes.user_routes import user_bp
from routes.stock_routes import stock_bp
from routes.trade_routes import trade_bp
from routes.holding_route import holding_bp
from routes.watchlist_route import watchlist_bp
from routes.order_route import order_bp
from routes.profile_route import profile_bp
from routes.transaction_route import transaction_bp

# Live in-memory price dictionaries populated by the Angel One WebSocket.
from data.live_data import LIVE_STOCKS, LIVE_INDEX

# -------------------------------------------------------------------
# App configuration
# -------------------------------------------------------------------
app = Flask(__name__)

# Secret key used to sign the session cookie.
# EVALUATOR NOTE: Move this to secrets.env in production.
app.secret_key = "an12eadf234f"

# Keep users logged in for 7 days without re-entering credentials.
app.permanent_session_lifetime = timedelta(days=7)
app.config.update(
    # Prevent JavaScript from reading the session cookie (XSS protection).
    SESSION_COOKIE_HTTPONLY=True,
    # 'Lax' allows the cookie to be sent on same-site navigations but not
    # cross-site requests (CSRF protection).
    SESSION_COOKIE_SAMESITE="Lax",
)

# -------------------------------------------------------------------
# Extension & Blueprint registration
# -------------------------------------------------------------------
socketio.init_app(app)  # Attach Flask-SocketIO to the app

# Each blueprint has a url_prefix that scopes all its routes.
app.register_blueprint(user_bp, url_prefix="/login")
app.register_blueprint(stock_bp, url_prefix="/stocks")
app.register_blueprint(trade_bp, url_prefix="/trade")
app.register_blueprint(holding_bp, url_prefix="/holding")
app.register_blueprint(transaction_bp, url_prefix="/transactions")
app.register_blueprint(watchlist_bp, url_prefix="/watchlist")
app.register_blueprint(order_bp, url_prefix="/order")
app.register_blueprint(profile_bp, url_prefix="/profile")

# -------------------------------------------------------------------
# Top-level routes
# -------------------------------------------------------------------

@app.route("/")
def home():
    """
    Landing page route.

    If the user is already logged in (session contains 'logged_in' and
    'user_id'), skip the landing page and redirect directly to the dashboard.
    Otherwise, render the public home.html marketing page.
    """
    if session.get("logged_in") and session.get("user_id"):
        return redirect("/login/dashboard")
    return render_template("home.html")


@app.route("/debug/routes")
def debug_routes():
    """
    Development helper: list all registered URL rules.

    Useful when diagnosing 404 errors after refactoring routes.
    Returns a JSON list of {rule, endpoint, methods} objects.
    Remove or protect this endpoint before deploying to production.
    """
    routes = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
        methods = sorted(m for m in rule.methods if m not in {"HEAD", "OPTIONS"})
        routes.append({"rule": rule.rule, "endpoint": rule.endpoint, "methods": methods})
    return jsonify({"routes": routes})


# -------------------------------------------------------------------
# Socket.IO event handlers
# -------------------------------------------------------------------

@socketio.on("connect")
def on_connect():
    """
    Triggered when a browser client establishes a WebSocket connection.

    Immediately emits the current live prices so the dashboard ticker
    populates instantly without waiting for the next scheduled broadcast.
    """
    print("🟢 Client connected")

    # Push the current snapshot of live prices to the newly connected client.
    socketio.emit("live_prices", {
        "stocks": LIVE_STOCKS,
        "index": LIVE_INDEX
    })