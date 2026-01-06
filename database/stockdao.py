from database.connection import get_connection as gc
from modal.Stock import Stock


def search_stocks(query):
    conn = gc()
    cur = conn.cursor()

    cur.execute("""
        SELECT stock_token, stock_name
        FROM stocks
        WHERE stock_short_name ILIKE %s
           OR stock_name ILIKE %s
        ORDER BY stock_short_name
        LIMIT 10
    """, (f"%{query}%", f"%{query}%"))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


def get_stock_by_token(stock_token):
    conn = gc()
    cur = conn.cursor()

    cur.execute("""
        SELECT stock_token, stock_name
        FROM stocks
        WHERE stock_token = %s
    """, (stock_token,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row