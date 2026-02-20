"""
routes/transaction_route.py
---------------------------
HTTP endpoint for retrieving a user's fund transaction history.

Blueprint prefix: /transactions
  GET /transactions/  → Return all ADD/WITHDRAW fund transactions as JSON.

This is distinct from trade orders; it only covers:
  - Funds added to the account.
  - Funds withdrawn from the account.
  - Amounts credited/debited when executing buy/sell trades.
"""

from flask import Blueprint, request, jsonify, render_template, session
from service.transaction_service import get_user_transactions

transaction_bp = Blueprint('transaction_bp', __name__)



@transaction_bp.route("/", methods=["GET"])
def transactions():
    """
    Retrieve all fund transactions for the authenticated user.

    The function manually serializes each DB row because the shape of the row
    tuple can vary (tuple unpacking with a fallback for safety).

    Returns:
      JSON: {"transactions": [list of dicts]} on success.
            {"error": ...} with HTTP 401/400 on failure.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    try:
        rows = get_user_transactions(user_id) or []

        serialized = []
        for row in rows:
            # Primary unpack; falls back to index-based access if shape is unexpected.
            try:
                transaction_id, row_user_id, amount, symbol_name, transaction_type, created_at = row
            except Exception:
                row = list(row)
                transaction_id = row[0] if len(row) > 0 else None
                row_user_id = row[1] if len(row) > 1 else None
                amount = row[2] if len(row) > 2 else None
                symbol_name = row[3] if len(row) > 3 else None
                transaction_type = row[4] if len(row) > 4 else None
                created_at = row[5] if len(row) > 5 else None

            # Convert datetime objects to ISO 8601 string so they are JSON-serialisable.
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat(sep=" ", timespec="seconds")

            serialized.append({
                "transaction_id": transaction_id,
                "user_id": row_user_id,
                "amount": amount,
                "symbol_name": symbol_name,
                "transaction_type": transaction_type,
                "created_at": created_at,
            })

        return jsonify({"transactions": serialized})
    except Exception as e:
        return jsonify({"error": str(e)}), 400