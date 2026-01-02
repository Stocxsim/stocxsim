from flask import Blueprint, request, jsonify,session
from modal.User import User
from service.userservice import login_service, signup_service , verify_otp, send_otp, getUserDetails

user_bp = Blueprint('user_bp', __name__)
    
@user_bp.route("/submit", methods=["POST"])
def email_verification():
    email = request.form.get('Email')
    user = login_service(email)
    return jsonify(user)

@user_bp.route("/save_user", methods=["POST"])
def save_user():
    email = request.form.get('Email')
    user = getUserDetails(email)
    session['email'] = user.get_email()
    session['username'] = user.get_username()
    session['user_id'] = user.get_user_id()


@user_bp.route("/signup", methods=["POST"])
def signup():
    email= request.form.get('Email')
    password= request.form.get('Password')
    username= request.form.get('Username')
    user=User(email, password, username)
    saved_user= signup_service(user)
    send_otp(email)
    return jsonify(saved_user)

@user_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    email = request.form.get('email')
    otp = request.form.get('otp')
    return jsonify({"message": verify_otp(email, otp)})