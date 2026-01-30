from database.connection import get_connection

DEFAULT_CATEGORY = "Watchlist"

# To get all stock tokens in a user's watchlist
def get_stock_tokens_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT stock_token FROM user_stocks WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]

# To check if a stock is in the user's watchlist


def safe_subscribe(user_id, stock_token):
    if not check_watchlist(user_id, stock_token):
        print(f"❌ Cannot subscribe {stock_token}, not in watchlist")
        return False  # Or return an error to the frontend
    # Otherwise, proceed with your subscription logic
    # ...
    return True

def check_watchlist(user_id, stock_token):
    stock_token = str(stock_token)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT 1 FROM user_stocks WHERE user_id=%s AND stock_token=%s AND  category=%s",
        (user_id, stock_token, DEFAULT_CATEGORY)
    )
    result = cur.fetchone()

    conn.close()
    print("🔥 in check_watchlist", result)
    return result is not None


# To add a stock to the user's watchlist
def add_to_watchlist(user_id, stock_token):
    stock_token = str(stock_token)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        " INSERT INTO user_stocks (user_id, stock_token, category) VALUES (%s, %s, %s) ON CONFLICT (user_id, stock_token) DO NOTHING",
        (user_id, stock_token, DEFAULT_CATEGORY)
    )

    conn.commit()
    conn.close()


# To remove a stock from the user's watchlist
def remove_from_watchlist(user_id, stock_token):
    stock_token = str(stock_token)
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM user_stocks WHERE user_id=%s AND stock_token=%s",
        (user_id, stock_token)
    )

    conn.commit()
    conn.close()
