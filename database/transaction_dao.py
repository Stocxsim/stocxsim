from database.connection import get_connection, return_connection

def insert_transaction(user_id,amount,  transaction_type,symbol_name=None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (user_id, amount, symbol, transaction_type)
            VALUES (%s, %s, %s, %s)
        """, (user_id, amount, symbol_name, transaction_type))
        conn.commit()
    finally:
        cur.close()
        return_connection(conn)

def get_transactions_by_user(user_id):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT transaction_id, user_id, amount, symbol, transaction_type, created_at
            FROM transactions
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        transactions = cur.fetchall()
        return transactions
    finally:
        cur.close()
        return_connection(conn)