from flask import Blueprint, request, jsonify
from service.userservice import login_service

user_bp = Blueprint('user_bp', __name__)

@user_bp.route("/submit", methods=["POST"])
def email_verification():
    email = request.form.get('Email')
    user = login_service(email)
    return jsonify(user)
