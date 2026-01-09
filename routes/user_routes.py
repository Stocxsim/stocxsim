from flask import Blueprint, request, jsonify,session,redirect, render_template
from modal.User import User
from service.userservice import login_service, signup_service , verify_otp, send_otp, getUserDetails
from websockets.angle_ws import subscribe_user_watchlist
from data.live_data import BASELINE_DATA
from database.user_stock_dao import get_stock_tokens_by_user 
from service.market_data_service import get_full_market_data, load_baseline_data


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
    tokens = get_stock_tokens_by_user(user_id)   # e.g. 20 tokens
    BASELINE_DATA.update(get_full_market_data(tokens))
    load_baseline_data()
    subscribe_user_watchlist(user_id, tokens)
    return jsonify({"success": True})


@user_bp.route("/signup", methods=["POST"])
def signup():
    email= request.form.get('Email')
    password= request.form.get('Password')
    username= request.form.get('Username')
    user=User(username, email, password)
    saved_user= signup_service(user)
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
    return render_template("/dashboard.html", username=session.get("username"), email=session.get("email"))


@user_bp.route("/holding")
def holdings():
    if not session.get("logged_in"):
        return redirect("/login")

    user = {
        "username": session.get("username"),
        "email": session.get("email"),
        "balance": session.get("balance", 0)  # default if missing
    }

    return render_template("holding.html", user=user)