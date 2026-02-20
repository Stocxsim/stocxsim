"""
service/transaction_service.py
------------------------------
Thin service layer over the transaction DAO.

Provides two operations:
  - record_transaction(): Save a new fund ADD/WITHDRAW or trade transaction.
  - get_user_transactions(): Fetch all transaction history for a user.
"""

from database.transaction_dao import get_transactions_by_user, insert_transaction

def record_transaction(user_id, amount, transaction_type, symbol_name=None):
    """
    Persist a transaction record to the database.

    Args:
        user_id          (int) : The user's ID.
        amount           (Decimal|float) : Transaction amount.
        transaction_type (str) : 'ADD', 'WITHDRAW', 'BUY', or 'SELL'.
        symbol_name      (str) : Optional stock name for trade transactions.
    """
    insert_transaction(user_id, amount, transaction_type, symbol_name)

def get_user_transactions(user_id):
    """
    Fetch all transactions for a given user from the database.

    Args:
        user_id (int): The user's ID.

    Returns:
        list of tuples: Each row represents one transaction record.
    """
    return get_transactions_by_user(user_id)