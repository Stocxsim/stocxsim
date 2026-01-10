from flask import Blueprint, jsonify, session
from service.holding_service import get_holdings_by_user


holding_bp = Blueprint('holding_bp', __name__)

@holding_bp.route("/order", methods=["POST"])
def get_user_holdings():
    try:
        user_id = session.get("user_id")

        holdings = get_holdings_by_user(user_id)

        return jsonify({
            "holdings": holdings
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400