from database.connection import get_connection, return_connection

DEFAULT_CATEGORY = "Watchlist"


def get_stock_tokens_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT stock_token, category FROM user_stocks WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [(row[0], row[1]) for row in rows]
    except Exception as e:
        return []
    finally:
        # Matches your return_connection function
        return_connection(conn)


def check_watchlist(user_id, stock_token):
    # Ensure token is a string for comparison consistency
    stock_token = str(stock_token)
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Use a CAST in SQL to ensure the database compares it correctly
        cur.execute(
            "SELECT 1 FROM user_stocks WHERE user_id=%s AND CAST(stock_token AS TEXT)=%s",
            (user_id, stock_token)
        )
        result = cur.fetchone()
        cur.close()
        return result is not None
    except Exception as e:
        return False
    finally:
        return_connection(conn)


def add_to_watchlist(user_id, stock_token):
    stock_token = str(stock_token)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO user_stocks (user_id, stock_token, category) VALUES (%s, %s, %s) "
            "ON CONFLICT (user_id, stock_token) DO NOTHING",
            (user_id, stock_token, DEFAULT_CATEGORY)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
    finally:
        return_connection(conn)


def remove_from_watchlist(user_id, stock_token):
    stock_token = str(stock_token)
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM user_stocks WHERE user_id=%s AND stock_token=%s",
            (user_id, stock_token)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
    finally:
        return_connection(conn)
