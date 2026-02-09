from database.connection import get_connection, return_connection
from modal.Stock import Stock


def search_stocks(query):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT stock_token, stock_name, stock_short_name, exchange
            FROM stocks
            WHERE stock_short_name ILIKE %s
               OR stock_name ILIKE %s
            ORDER BY stock_short_name
            LIMIT 10
        """, (f"%{query}%", f"%{query}%"))

        rows = cur.fetchall()
        return rows
    finally:
        cur.close()
        return_connection(conn)


def get_stock_by_token(stock_token):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT stock_token, stock_name
            FROM stocks
            WHERE stock_token = %s
        """, (stock_token,))

        row = cur.fetchone()
        return row
    finally:
        cur.close()
        return_connection(conn)

def get_stock_short_name_by_token(stock_token):
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT stock_short_name
            FROM stocks
            WHERE stock_token = %s
        """, (stock_token,))

        row = cur.fetchone()
        if row:
            return row[0]
        return None
    finally:
        cur.close()
        return_connection(conn)