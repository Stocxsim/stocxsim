from flask import Blueprint, request, jsonify, render_template, session
from service.transaction_service import get_user_transactions

transaction_bp = Blueprint('transaction_bp', __name__)


@transaction_bp.route("/", methods=["GET"])
def transactions():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not logged in"}), 401
    try:
        rows = get_user_transactions(user_id) or []

        serialized = []
        for row in rows:
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