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


def get_weekly_orders(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT DATE_TRUNC('week', created_at) AS week_start,
                COUNT(order_id) AS total_orders
                FROM orders
                where user_id = %s
                GROUP BY week_start
                ORDER BY week_start;
        """

        cursor.execute(query, (user_id,))
        orders = cursor.fetchall()
        week_start=[order[0].strftime("%Y-%m-%d") for order in orders]
        total_orders=[order[1] for order in orders]
        return {
            "week_start": week_start,
            "total_orders": total_orders
        }
    finally:
        cursor.close()
        return_connection(conn)


def get_orders_sorted(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT symbol_token, transaction_type, quantity, price, created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at ASC;
        """

        cursor.execute(query, (user_id,))
        orders = cursor.fetchall()
        order_list = []
        for ord in orders:
            order_list.append({
                "symbol_token": ord[0],
                "transaction_type": ord[1],
                "quantity": ord[2],
                "price": ord[3],
                "created_at": ord[4]
            })
        return order_list

    finally:
        cursor.close()
        return_connection(conn)


# Search order filter
def search_order(query_text):
    conn = get_connection()
    cursor = conn.cursor()

    try:

        sql = """
            SELECT 
                s.stock_short_name, 
                o.transaction_type, 
                o.quantity, 
                o.price, 
                o.created_at, 
                o.order_type,
                s.stock_name
            FROM orders o
            JOIN stocks s ON o.symbol_token = s.stock_token
            WHERE s.stock_short_name ILIKE %s 
               OR s.stock_name ILIKE %s
            ORDER BY o.created_at DESC
            LIMIT 10;
        """

        search_val = f"%{query_text}%"
        cursor.execute(sql, (search_val, search_val))
        orders = cursor.fetchall()
        print("its happening")
        return orders
    except Exception as e:
        # CHECK YOUR TERMINAL: This will print exactly what went wrong
        print("--- DATABASE CRASH ---")
        print(f"Error: {e}") 
        print("----------------------")
        return []

    finally:
        cursor.close()
        return_connection(conn)