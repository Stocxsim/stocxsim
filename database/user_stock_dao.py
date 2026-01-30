from database.connection import get_connection, return_connection

def get_stock_tokens_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT stock_token FROM user_stocks WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        return [row[0] for row in rows]
    finally:
        cursor.close()
        return_connection(conn)
    