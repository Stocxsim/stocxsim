from flask import Blueprint, request, jsonify, session, redirect, render_template
from decimal import Decimal, InvalidOperation
import threading
import time
from modal.User import User
from service.userservice import login_service, signup_service, verify_otp_service, send_otp, getUserDetails
from database.watchlist_dao import get_stock_tokens_by_user
from service.market_data_service import get_full_market_data, load_baseline_data
from websockets.angle_ws import subscribe_equity_tokens, subscribe_user_watchlist
from data.live_data import register_equity_token, ensure_baseline_data, BASELINE_DATA
from database.watchlist_dao import get_stock_tokens_by_user
from database.userdao import checkBalance, updateBalance, updatePassword
from service.transaction_service import record_transaction

from utils.tokens import INDEX_TOKENS


user_bp = Blueprint('user_bp', __name__)


def _parse_amount_from_request() -> Decimal:
    """Parse amount from JSON body, form, or querystring."""
    if request.is_json:
        payload = request.get_json(silent=True) or {}
        raw = payload.get("amount", "0")
    else:
        raw = request.form.get("amount") or request.args.get("amount", "0")

    try:
        return Decimal(str(raw))
    except (InvalidOperation, TypeError):
        raise ValueError("invalid_amount")

_post_login_init_lock = threading.Lock()
_post_login_init_inflight = set()


def _trigger_post_login_init(user_id: int) -> None:
    """Idempotent, restart-safe post-login initialization.

    Runs in background to avoid hanging requests. Safe to call on every page load.
    """
    if not user_id:
        return

    with _post_login_init_lock:
        if user_id in _post_login_init_inflight:
            return
        _post_login_init_inflight.add(user_id)

    def _run():
        try:
            tokens = [str(t[0]) for t in get_stock_tokens_by_user(user_id)]
            tokens = [t for t in tokens if t not in INDEX_TOKENS]
            for token in tokens:
                register_equity_token(token)

            # Baseline can be fetched even if WS isn't ready yet.
            try:
                ensure_baseline_data(tokens)
            except Exception:
                pass

            # WS may still be connecting after an app restart; retry briefly.
            for _ in range(20):  # ~10s total
                try:
                    subscribe_equity_tokens(tokens)
                    subscribe_user_watchlist(user_id, tokens)
                except Exception:
                    pass
                time.sleep(0.5)
        finally:
            with _post_login_init_lock:
                _post_login_init_inflight.discard(user_id)

    threading.Thread(target=_run, daemon=True).start()


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

    # Persist auth across browser restarts (within permanent_session_lifetime)
    session.permanent = True

    # 🔥 SUBSCRIBE USER WATCHLIST
    user_id = user.get_user_id()
    tokens = [str(t[0]) for t in get_stock_tokens_by_user(user_id)]   # e.g. 20 tokens
    tokens = [t for t in tokens if t not in INDEX_TOKENS]

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

    # Kick off init that is safe on restarts/reloads.
    _trigger_post_login_init(user_id)

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
    result = verify_otp_service(email, otp)
    print(result)
    return jsonify({"message": result})


@user_bp.route("/forgot/send-otp", methods=["POST"])
def forgot_send_otp():
    email = (request.form.get("Email") or request.form.get("email") or "").strip()
    if not email:
        return jsonify({"success": False, "error": "email_required"}), 400

    user = getUserDetails(email)
    if not user:
        return jsonify({"success": False, "error": "user_not_found"}), 404

    send_otp(email)
    return jsonify({"success": True})


@user_bp.route("/forgot/reset", methods=["POST"])
def forgot_reset_password():
    email = (request.form.get("email") or request.form.get("Email") or "").strip()
    otp = (request.form.get("otp") or "").strip()
    new_pass = request.form.get("new_password") or ""
    confirm_pass = request.form.get("confirm_password") or ""

    if not email or not otp:
        return jsonify({"success": False, "error": "missing_fields"}), 400
    if not new_pass or not confirm_pass:
        return jsonify({"success": False, "error": "missing_password"}), 400
    if new_pass != confirm_pass:
        return jsonify({"success": False, "error": "password_mismatch"}), 400

    user = getUserDetails(email)
    if not user:
        return jsonify({"success": False, "error": "user_not_found"}), 404

    verified = verify_otp_service(email, otp)
    if not verified:
        return jsonify({"success": False, "error": "invalid_otp"}), 400

    updatePassword(user.get_user_id(), new_pass)
    return jsonify({"success": True})


@user_bp.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect("/")

    # Resume-safe init: on app restart, this makes WS/subscriptions catch up.
    _trigger_post_login_init(session.get("user_id"))
    user = {
        "username": session.get("username"),
        "email": session.get("email"),
        "balance": checkBalance(session.get("user_id"))
    }

    return render_template("dashboard.html", user=user, active_tab="explore")


@user_bp.route("/status")
def auth_status():
    is_authed = bool(session.get("logged_in") and session.get("user_id"))
    return jsonify({"authenticated": is_authed})


@user_bp.route("/holding")
def holdings():
    if not session.get("logged_in"):
        return redirect("/")

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
        return redirect("/")

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
        return redirect("/")

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
    return jsonify({"balance": str(balance if balance is not None else 0)})

@user_bp.route("/add_funds", methods=["GET", "POST"])
def add_funds():
    if not session.get("logged_in") or "user_id" not in session:
        if request.method == "POST":
            return jsonify({"error": "unauthorized"}), 401
        return redirect("/")

    try:
        amount = _parse_amount_from_request()
    except ValueError:
        if request.method == "POST":
            return jsonify({"error": "invalid_amount"}), 400
        return redirect("/profile/funds?error=invalid_amount")

    if amount <= 0:
        if request.method == "POST":
            return jsonify({"error": "invalid_amount"}), 400
        return redirect("/profile/funds?error=invalid_amount")

    user_id = session["user_id"]
    current_balance = Decimal(str(checkBalance(user_id) or 0))
    new_balance = current_balance + amount

    updateBalance(user_id, new_balance)
    record_transaction(user_id, amount, "ADD")
    if request.method == "POST":
        return jsonify({"success": True, "balance": str(new_balance)})
    return redirect("/profile/funds?success=added")


@user_bp.route("/withdraw_funds", methods=["GET", "POST"])
def withdraw_funds():
    if not session.get("logged_in") or "user_id" not in session:
        if request.method == "POST":
            return jsonify({"error": "unauthorized"}), 401
        return redirect("/")

    try:
        amount = _parse_amount_from_request()
    except ValueError:
        if request.method == "POST":
            return jsonify({"error": "invalid_amount"}), 400
        return redirect("/profile/funds?error=invalid_amount")

    if amount <= 0:
        if request.method == "POST":
            return jsonify({"error": "invalid_amount"}), 400
        return redirect("/profile/funds?error=invalid_amount")

    user_id = session["user_id"]
    current_balance = Decimal(str(checkBalance(user_id) or 0))

    if current_balance < amount:
        if request.method == "POST":
            return jsonify({"error": "insufficient_balance", "balance": str(current_balance)}), 400
        return redirect("/profile/funds?error=insufficient_balance")

    new_balance = current_balance - amount
    updateBalance(user_id, new_balance)
    record_transaction(user_id, amount, "WITHDRAW")
    if request.method == "POST":
        return jsonify({"success": True, "balance": str(new_balance)})
    return redirect("/profile/funds?success=withdrawn")