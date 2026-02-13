from database.connection import get_connection, return_connection
from data.live_data import LIVE_STOCKS, BASELINE_DATA


def add_holding(order_details):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Check if the holding already exists
        query_check = """
        SELECT quantity , avg_buy_price FROM holdings WHERE user_id = %s AND symbol_token = %s AND order_type = %s
        """
        cursor.execute(
            query_check, (order_details["user_id"], order_details["symbol_token"], order_details["order_type"]))
        result = cursor.fetchone()

        if result:
            # Update existing holding
            new_quantity = result[0] + order_details["quantity"]
            query_update = """
            UPDATE holdings SET quantity = %s , avg_buy_price = %s WHERE user_id = %s AND symbol_token = %s AND order_type = %s
            """
            new_avg_price = ((result[1] * result[0]) + (order_details["price"]
                             * order_details["quantity"])) / new_quantity
            cursor.execute(query_update, (new_quantity, new_avg_price,
                           order_details["user_id"], order_details["symbol_token"], order_details["order_type"]))
        else:
            # Insert new holding
            query_insert = """
            INSERT INTO holdings (user_id, symbol_token, quantity, avg_buy_price,order_type)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                query_insert, (order_details["user_id"], order_details["symbol_token"], order_details["quantity"], order_details["price"], order_details["order_type"]))
        conn.commit()
    finally:
        cursor.close()
        return_connection(conn)


def update_holding_on_sell(order_details):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Fetch current holding
        query_check = """
        SELECT quantity FROM holdings WHERE user_id = %s AND symbol_token = %s AND order_type = %s
        """
        cursor.execute(
            query_check, (order_details["user_id"], order_details["symbol_token"], order_details["order_type"]))
        result = cursor.fetchone()

        if result:
            current_quantity = result[0]
            sell_quantity = order_details["quantity"]

            # 🔴 MAIN VALIDATION (THIS WAS MISSING)
            if sell_quantity > current_quantity:
                return False, "Insufficient quantity to sell"
            new_quantity = current_quantity - sell_quantity

            if new_quantity > 0:
                # Update holding with reduced quantity
                query_update = """
                UPDATE holdings SET quantity = %s WHERE user_id = %s AND symbol_token = %s AND order_type = %s
                """
                cursor.execute(query_update, (new_quantity,
                               order_details["user_id"], order_details["symbol_token"], order_details["order_type"]))
                conn.commit()
            else:
                # Remove holding if quantity is zero or less
                query_delete = """
                DELETE FROM holdings WHERE user_id = %s AND symbol_token = %s AND order_type = %s
                """
                cursor.execute(
                    query_delete, (order_details["user_id"], order_details["symbol_token"], order_details["order_type"]))
                conn.commit()
            return True
        else:
            return False
    finally:
        cursor.close()
        return_connection(conn)


# This is for holding page, that give data of all holding for perticulat account
def get_holdings_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        query = """
        SELECT h.holding_id, h.symbol_token, h.quantity, h.avg_buy_price,h.order_type,
               s.stock_name, s.stock_short_name
        FROM holdings h
        LEFT JOIN stocks s ON s.stock_token = h.symbol_token
        WHERE h.user_id = %s
        """
        cursor.execute(query, (user_id,))
        holdings = cursor.fetchall()
        holdings_dict = {}

        for holding in holdings:
            holding_id = holding[0]
            token_str = str(holding[1])

            live = LIVE_STOCKS.get(token_str) or {}
            base = BASELINE_DATA.get(token_str) or {}
            market_price = live.get("ltp")
            if market_price is None:
                market_price = base.get("ltp")
            if market_price is None:
                market_price = base.get("prev_close")
            if market_price is None:
                market_price = 0

            holdings_dict[holding_id] = {
                "symbol_token": holding[1],
                "quantity": holding[2],
                "avg_buy_price": holding[3],
                "market_price": market_price,
                "prev_close": (base.get("prev_close") if base else None),
                "stock_name": holding[5],
                "stock_short_name": holding[6],
                "order_type": holding[4],
            }
        return holdings_dict
    finally:
        cursor.close()
        return_connection(conn)


# This is for stock page, that give data of single holding for perticulat stock token and user
def get_holding_by_user_and_token(user_id, symbol_token):
    """Return a single holding row (quantity, avg_buy_price) for a user/token."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT quantity, avg_buy_price, order_type
            FROM holdings
            WHERE user_id = %s AND symbol_token = %s
            """,
            (user_id, symbol_token),
        )
        rows = cursor.fetchall()

        # There is chance of 2 types of holding for same stock token (1 for market and 1 for mtf), so we will return default 0 holding if no row found, and stock page will decide which one to show based on order type.
        holdings_data = {
            "market": {"quantity": 0, "avg_buy_price": 0},
            "mtf": {"quantity": 0, "avg_buy_price": 0}
        }

        for row in rows:
            qty, avg_price, o_type = row
            if o_type in holdings_data:
                holdings_data[o_type] = {
                    "quantity": qty,
                    "avg_buy_price": float(avg_price)
                }

        return holdings_data
    finally:
        cursor.close()
        return_connection(conn)
