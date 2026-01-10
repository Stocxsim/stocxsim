from database.connection import get_connection
from database.stockdao import get_stock_by_token

def add_holding(order_details):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if the holding already exists
    query_check = """
    SELECT quantity , avg_buy_price FROM holdings WHERE user_id = %s AND symbol_token = %s
    """
    cursor.execute(query_check, (order_details["user_id"], order_details["symbol_token"]))
    result = cursor.fetchone()

    if result:
        # Update existing holding
        new_quantity = result[0] + order_details["quantity"]
        query_update = """
        UPDATE holdings SET quantity = %s , avg_buy_price = %s WHERE user_id = %s AND symbol_token = %s
        """
        new_avg_price = ((result[1] * result[0]) + (order_details["price"] * order_details["quantity"])) / new_quantity
        cursor.execute(query_update, (new_quantity, new_avg_price, order_details["user_id"], order_details["symbol_token"]))
    else:
        # Insert new holding
        query_insert = """
        INSERT INTO holdings (user_id, symbol_token, quantity, avg_buy_price)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_insert, (order_details["user_id"], order_details["symbol_token"], order_details["quantity"], order_details["price"]))

    conn.commit()
    cursor.close()
    conn.close()

def update_holding_on_sell(order_details):
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch current holding
    query_check = """
    SELECT quantity FROM holdings WHERE user_id = %s AND symbol_token = %s
    """
    cursor.execute(query_check, (order_details["user_id"], order_details["symbol_token"]))
    result = cursor.fetchone()

    if result:
        current_quantity = result[0]
        new_quantity = current_quantity - order_details["quantity"]

        if new_quantity > 0:
            # Update holding with reduced quantity
            query_update = """
            UPDATE holdings SET quantity = %s WHERE user_id = %s AND symbol_token = %s
            """
            cursor.execute(query_update, (new_quantity, order_details["user_id"], order_details["symbol_token"]))
        else:
            # Remove holding if quantity is zero or less
            query_delete = """
            DELETE FROM holdings WHERE user_id = %s AND symbol_token = %s
            """
            cursor.execute(query_delete, (order_details["user_id"], order_details["symbol_token"]))
            conn.commit()
            cursor.close()
            conn.close()
        return True
    else:    
        cursor.close()
        conn.close()
        return False

def get_holdings_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT symbol_token, quantity, avg_buy_price FROM holdings WHERE user_id = %s
    """
    cursor.execute(query, (user_id,))
    holdings = cursor.fetchall()

    cursor.close()
    conn.close()

    holdings_dict = {}
    for holding in holdings:
        holdings_dict[get_stock_by_token(holding[0])[1]] = {
            "symbol_token": holding[0],
            "quantity": holding[1],
            "avg_buy_price": holding[2]
        }
    return holdings_dict