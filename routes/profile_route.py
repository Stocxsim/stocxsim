"""
routes/profile_route.py
-----------------------
HTTP endpoints for user profile management.

Blueprint prefix: /profile
  GET  /profile/         → Render the profile page.
  GET  /profile/funds    → Render the funds (add/withdraw) page.
  POST /profile/update-name      → Change the user's display name.
  POST /profile/update-password  → Change the user's password.
"""

from flask import Blueprint, render_template, session, redirect, request, jsonify
from service.userservice import getUserDetails
from database.userdao import checkBalance
from database.userdao import updateUsername
from database.userdao import updatePassword

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/")
def profile():
    """
    Render the user's profile page.

    Redirects to the dashboard if the user is not authenticated.
    Fetches the full user object from DB (not just session data) to ensure
    we display the most up-to-date username and balance.
    """
    if "email" not in session:
        return redirect("/login/dashboard")

    # getUserDetails expects the email address to look up the user.
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
    """
    Render the funds management page where users can add or withdraw balance.

    Uses a local import for checkBalance here to avoid any circular import
    since userdao is also imported at the top.
    """
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
    """
    Update the current user's display name.

    Expects JSON body: {"name": "new_username"}
    Also updates the session's 'username' key so subsequent page renders
    show the new name without requiring a re-login.
    """
    if "email" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    new_name = data.get("name")

    if not new_name:
        return jsonify({"error": "Invalid name"}), 400

    user_obj = getUserDetails(session["email"])
    if not user_obj:
        return jsonify({"error": "User not found"}), 404

    # Persist the new username to the database.
    updateUsername(user_obj.get_user_id(), new_name)

    # Keep the session in sync so the navbar shows the updated name immediately.
    session["username"] = new_name

    return jsonify({"success": True})


@profile_bp.route("/update-password", methods=["POST"])
def update_password():
    """
    Change the current user's password.

    Expects JSON body: {"new_password": "...", "confirm_password": "..."}
    Both passwords must match before the update is applied.
    """
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

