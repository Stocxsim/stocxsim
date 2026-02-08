from database.transaction_dao import get_transactions_by_user, insert_transaction

def record_transaction(user_id, amount, transaction_type, symbol_name=None):
    insert_transaction(user_id, amount, transaction_type, symbol_name)

def get_user_transactions(user_id):
    return get_transactions_by_user(user_id)