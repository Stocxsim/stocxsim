from flask import Blueprint, render_template

orders_bp = Blueprint("orders_bp", __name__)

class DUser:
    def __init__(self, username=None, email=None, balance=0):
        self.username = username
        self.email = email
        self.balance = balance

@orders_bp.route("/orders")
def orders():
    user = DUser(
        username="Parth",
        email="parth@example.com",
        balance=50000
    )

    # ✅ MUST return render_template
    return render_template(
        "orders.html",
        active_tab="orders",
        user=user
    )
