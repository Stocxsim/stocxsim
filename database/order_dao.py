import datetime
from database.connection import get_connection, return_connection
from datastructure.stack import *
from modal.Order import Order

def insert_order(order_details):
    conn = get_connection()
    try:
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
    finally:
        cursor.close()
        return_connection(conn)

from datetime import datetime

def get_order(user_id, filter_params=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        query = """
            SELECT order_id, symbol_token, transaction_type,
                   quantity, price, order_type, created_at
            FROM orders
            WHERE user_id = %s
        """

        values = [user_id]
        conditions = []

        if filter_params:
            # ✅ Date handling
            from_date = filter_params.get("from_date")
            to_date = filter_params.get("to_date")

            if from_date or to_date:
                if not from_date:
                    from_date = "1970-01-01"

                if not to_date:
                    to_date = datetime.today().strftime("%Y-%m-%d")

                conditions.append("DATE(created_at) BETWEEN %s AND %s")
                values.extend([from_date, to_date])

            # ✅ BUY / SELL filter
            transaction_type = filter_params.get("transaction_type")
            if transaction_type:
                placeholders = ", ".join(["%s"] * len(transaction_type))
                conditions.append(f"transaction_type IN ({placeholders})")
                values.extend(transaction_type)

        # ✅ Apply conditions
        if conditions:
            query += " AND " + " AND ".join(conditions)

        cursor.execute(query, tuple(values))
        orders = cursor.fetchall()

        stack = Stack()
        for ord in orders:
            order = Order(
                order_id=ord[0],
                user_id=user_id,
                symbol_token=ord[1],
                transaction_type=ord[2],
                quantity=ord[3],
                price=ord[4],
                order_type=ord[5],
                created_at=ord[6]
            )
            stack.push(order)
        return stack

    finally:
        cursor.close()
        return_connection(conn)
