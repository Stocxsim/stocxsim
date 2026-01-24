import datetime
from database.connection import get_connection
from datastructure.stack import *
from modal.Order import Order

def insert_order(order_details):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO orders (user_id, symbol_token, transaction_type, quantity, price, order_type)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        order_details["user_id"],
        order_details["symbol_token"],
        order_details["transaction_type"],
        order_details["quantity"],
        order_details["price"],
        order_details["order_type"],
    ))

    conn.commit()
    cursor.close()
    conn.close()

def get_order(user_id,filter_params=None):
    conn = get_connection()
    cursor = conn.cursor()

    
    filter_params = {
        "from_date": "2024-01-01",
        "to_date": "2024-01-25",
        "transaction_type": ["BUY", "SELL"]
    }
    query = "SELECT order_id, symbol_token, transaction_type, quantity, price, order_type, created_at FROM orders WHERE user_id = %s"
    if filter_params:
        conditions = []
        values = [user_id]

        # Case 1: From exists but To missing → set To = Today
        if "from_date" in filter_params and not "to_date" in filter_params:
            to_date = datetime.today().strftime("%Y-%m-%d")
            conditions.append("created_at BETWEEN %s AND %s")
            values.append(filter_params["from_date"])
            values.append(to_date)

        if not "from_date" in filter_params and "to_date" in filter_params:
            from_date = "1970-01-01"
            conditions.append("created_at BETWEEN %s AND %s")
            values.append(from_date)
            values.append(filter_params["to_date"])

        if "from_date" in filter_params and "to_date" in filter_params:
            conditions.append("created_at BETWEEN %s AND %s")
            values.append(filter_params["from_date"])
            values.append(filter_params["to_date"])

        if filter_params.get("transaction_type") and len(filter_params["transaction_type"]) > 0:
            placeholders = ', '.join(['%s'] * len(filter_params["transaction_type"]))
            conditions.append(f"transaction_type IN ({placeholders})")
            values.extend(filter_params["transaction_type"])

        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(values))
        orders = cursor.fetchall()
        stack = Stack()
        for ord in orders:
            order=Order(
                order_id=ord[0],
                user_id=user_id,
                symbol_token=ord[1],
                transaction_type=ord[2],
                price=ord[4],
                quantity=ord[3],
                order_type=ord[5],
                created_at=ord[6]
            )
            stack.push(order)
        cursor.close()
        conn.close()
        return stack
        

    else:
        cursor.execute(query, (user_id,))
        orders = cursor.fetchall()
        stack = Stack()
        for ord in orders:
            order=Order(
                order_id=ord[0],
                user_id=user_id,
                symbol_token=ord[1],
                transaction_type=ord[2],
                price=ord[4],
                quantity=ord[3],
                order_type=ord[5],
                created_at=ord[6]
            )
            stack.push(order)
        cursor.close()
        conn.close()
        return stack
    
