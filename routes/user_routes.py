from flask import Blueprint, request, jsonify, session, redirect, render_template
from decimal import Decimal, InvalidOperation
import threading
from modal.User import User
from service.userservice import login_service, signup_service, verify_otp, send_otp, getUserDetails
from database.watchlist_dao import get_stock_tokens_by_user
from service.market_data_service import get_full_market_data, load_baseline_data
from websockets.angle_ws import subscribe_equity_tokens, subscribe_user_watchlist
from data.live_data import register_equity_token, ensure_baseline_data, BASELINE_DATA
from database.watchlist_dao import get_stock_tokens_by_user
from database.userdao import checkBalance, updateBalance


user_bp = Blueprint('user_bp', __name__)


@user_bp.route("/submit", methods=["POST"])
def email_verification():
    email = request.form.get('Email')
    user = login_service(email)
    return jsonify(user)


@user_bp.route("/save-user", methods=["POST"])
def save_user():
    email = request.form.get('Email')
    password = request.form.get('Password')
    user = getUserDetails(email)
    if user.get_password() != password:
        return jsonify({"success": False})

    session['logged_in'] = True
    session['email'] = user.get_email()
    session['username'] = user.get_username()
    session['user_id'] = user.get_user_id()

    # 🔥 SUBSCRIBE USER WATCHLIST
    user_id = user.get_user_id()
    tokens = [str(t[0]) for t in get_stock_tokens_by_user(user_id)]   # e.g. 20 tokens

    # Keep login response fast: do live-data warmup in background.
    for token in tokens:
        register_equity_token(token)

    def _warm_watchlist():
        try:
            subscribe_equity_tokens(tokens)
            ensure_baseline_data(tokens)
        except Exception:
            # Never block login due to market-data issues.
            return

    threading.Thread(target=_warm_watchlist, daemon=True).start()

    return jsonify({"success": True})


@user_bp.route("/signup", methods=["POST"])
def signup():
    email = request.form.get('Email')
    password = request.form.get('Password')
    username = request.form.get('Username')
    user = User(username, email, password)
    saved_user = signup_service(user)
    send_otp(email)
    return jsonify(saved_user)


@user_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    email = request.form.get('email')
    otp = request.form.get('otp')
    result = verify_otp(email, otp)
    return jsonify({"message": result})


@user_bp.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/login")
    user = {
        "username": session.get("username"),
        "email": session.get("email"),
        "balance": checkBalance(session.get("user_id"))
    }

    return render_template("dashboard.html", user=user, active_tab="explore")


@user_bp.route("/holding")
def holdings():
    if not session.get("logged_in"):
        return redirect("/login")

    user = {
        "username": session.get("username"),
        "email": session.get("email"),
        "balance": checkBalance(session.get("user_id"))
    }

    return render_template("holding.html", user=user, active_tab="holdings")

# NOTE - this is for watchlist page button, not for the Watchlist data itself.
# this is login/watchlist not stocks/watchlist
# this is for rendering the watchlist page
@user_bp.route("/watchlist")
def watchlist():
    if not session.get("logged_in"):
        return redirect("/login")

    user = {
        "username": session.get("username"),
        "email": session.get("email"),
        "balance": checkBalance(session.get("user_id"))
    }

    return render_template(
        "watchlist.html",
        user=user,
        active_tab="watchlist"
    )

@user_bp.route("/orders")
def orders():
    if not session.get("logged_in"):
        return redirect("/login")

    user = {
        "username": session.get("username"),
        "email": session.get("email"),
        "balance": checkBalance(session.get("user_id"))
    }

    return render_template(
        "orders.html",
        user=user,
        active_tab="orders"
    )


@user_bp.route('/logout', methods=['POST'])
def logout():
    session.clear() 
    return jsonify({"success": True}), 200


@user_bp.route("/get-balance")
def get_balance():
    if 'user_id' not in session:
        return jsonify({"error": "User not logged in"}), 401
    
    balance = checkBalance(session['user_id'])
    return jsonify({"balance": balance})

@user_bp.route("/add_funds")
def add_funds():
    if not session.get("logged_in") or "user_id" not in session:
        return redirect("/login")

    amount_raw = request.args.get("amount", "0")
    try:
        amount = Decimal(str(amount_raw))
    except (InvalidOperation, TypeError):
        return redirect("/profile/funds?error=invalid_amount")

    if amount <= 0:
        return redirect("/profile/funds?error=invalid_amount")

    user_id = session["user_id"]
    current_balance = Decimal(str(checkBalance(user_id) or 0))
    new_balance = current_balance + amount

    updateBalance(user_id, new_balance)
    return redirect("/profile/funds?success=added")


@user_bp.route("/withdraw_funds")
def withdraw_funds():
    if not session.get("logged_in") or "user_id" not in session:
        return redirect("/login")

    amount_raw = request.args.get("amount", "0")
    try:
        amount = Decimal(str(amount_raw))
    except (InvalidOperation, TypeError):
        return redirect("/profile/funds?error=invalid_amount")

    if amount <= 0:
        return redirect("/profile/funds?error=invalid_amount")

    user_id = session["user_id"]
    current_balance = Decimal(str(checkBalance(user_id) or 0))

    if current_balance < amount:
        return redirect("/profile/funds?error=insufficient_balance")

    new_balance = current_balance - amount
    updateBalance(user_id, new_balance)
    return redirect("/profile/funds?success=withdrawn")
