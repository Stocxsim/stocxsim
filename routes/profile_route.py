from flask import Blueprint, render_template, session, redirect
from service.userservice import getUserDetails
from database.userdao import checkBalance

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
