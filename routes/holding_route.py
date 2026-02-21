"""
routes/holding_route.py
-----------------------
HTTP endpoint for fetching the currently logged-in user's portfolio holdings.

Blueprint prefix: /holding
  POST /holding/order  → return all holdings as JSON for the frontend to
                         render the Portfolio / Holdings page table.

When holdings are fetched:
  1. All held stock tokens are registered for live-price updates.
  2. Tokens are subscribed to the Angel One WebSocket for real-time LTP.
  3. Baseline (REST) price data is fetched in a background thread.
"""

from flask import Blueprint, jsonify, session
import threading
from database.holding_dao import get_holdings_by_user
from data.live_data import register_equity_token, ensure_baseline_data
from websockets.angle_ws import subscribe_equity_tokens


holding_bp = Blueprint('holding_bp', __name__)



@holding_bp.route("/order", methods=["POST"])
def get_user_holdings():
    """
    Fetch all holdings for the current user and prepare them for live updates.

    Returns:
      JSON: {"holdings": { symbol → holding_dict }} on success.
            {"error": ...} with HTTP 401 if not authenticated.
    """
    try:
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "User not logged in"}), 401

        holdings = get_holdings_by_user(user_id)
        tokens = []

        # Register each held stock token so the live-data layer tracks it.
        for symbol, h in holdings.items():
            token = str(h["symbol_token"])
            tokens.append(token)
            register_equity_token(token)

        # Subscribe holdings tokens to Angel WS (non-blocking) so Socket.IO emits updates.
        subscribe_equity_tokens(tokens)

        # Ensure we have baseline data for holdings; run in background to keep API fast.
        threading.Thread(target=ensure_baseline_data, args=(tokens,), daemon=True).start()
        return jsonify({
            "holdings": holdings
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400
