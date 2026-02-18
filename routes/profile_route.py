from flask import Blueprint, render_template, session, redirect,request, jsonify
from service.userservice import getUserDetails
from database.userdao import checkBalance
from database.userdao import updateUsername
from database.userdao import updatePassword
profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/")
def profile():
    if "email" not in session:
        return redirect("/login/dashboard")

    # 🔥 userservice expects EMAIL
    user_obj = getUserDetails(session["email"])

    if not user_obj:
        return redirect("/login/dashboard")

    balance = checkBalance(user_obj.get_user_id())

    user = {
        "username": user_obj.get_username(),
        "email": user_obj.get_email(),
        "balance": balance
    }

    return render_template("profile.html", user=user)

@profile_bp.route("/funds")
def funds():
    if "email" not in session:
        return redirect("/login/dashboard")

    user_obj = getUserDetails(session["email"])
    if not user_obj:
        return redirect("/login/dashboard")

    from database.userdao import checkBalance
    balance = checkBalance(user_obj.get_user_id())

    user = {
        "username": user_obj.get_username(),
        "email": user_obj.get_email(),
        "balance": balance
    }

    return render_template(
        "funds.html",
        user=user,
        active_tab=None
    )

@profile_bp.route("/update-name", methods=["POST"])
def update_name():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    new_name = data.get("name")

    if not new_name:
        return jsonify({"error": "Invalid name"}), 400

    user_obj = getUserDetails(session["email"])
    if not user_obj:
        return jsonify({"error": "User not found"}), 404

    # 🔥 database update
    updateUsername(user_obj.get_user_id(), new_name)

    session["username"] = new_name

    return jsonify({"success": True})

@profile_bp.route("/update-password", methods=["POST"])
def update_password():
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    new_pass = data.get("new_password")
    confirm_pass = data.get("confirm_password")

    if not new_pass or not confirm_pass:
        return jsonify({"error": "Invalid input"}), 400

    if new_pass != confirm_pass:
        return jsonify({"error": "Passwords do not match"}), 400

    user_obj = getUserDetails(session["email"])
    if not user_obj:
        return jsonify({"error": "User not found"}), 404

    updatePassword(user_obj.get_user_id(), new_pass)

    return jsonify({"success": True})

