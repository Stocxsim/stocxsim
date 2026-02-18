from database.connection import get_connection as gc, return_connection
from modal.User import User

def existUser(email):
    query = "SELECT * FROM users WHERE email = %s"
    conn = gc()
    try:
        cur = conn.cursor()
        cur.execute(query, (email,))
        result = cur.fetchone()
        if result is not None:
            query="SELECT password FROM users WHERE email=%s"
            cur.execute(query,(email,))
            password=cur.fetchone()
            
            return {"message":True,"password":password[0]}
        else:
            return {"message":False,"password":None}
    finally:
        cur.close()
        return_connection(conn)
    
def saveUser(user):
    try:
        conn = gc()
        cur = conn.cursor()

        query = """
        INSERT INTO users (user_name, email, password,balance)
        VALUES (%s, %s, %s,%s)
        """

        cur.execute(query, (user.username, user.email, user.password,100000))
        conn.commit()
        return {"message": True}

    except Exception as e:
        return {"message": False}

    finally:
        cur.close()
        return_connection(conn)

def getUserByEmail(email):
    query = "SELECT user_id,user_name,email,password FROM users WHERE email = %s"
    conn = gc()
    try:
        cur = conn.cursor()
        cur.execute(query, (email,))
        result = cur.fetchone()
        if result is not None:
            user=User(result[1],result[2],result[3],result[0])
            return user
        else:
            return None
    finally:
        cur.close()
        return_connection(conn)
    
def checkBalance(user_id):
    query = "SELECT balance FROM users WHERE user_id = %s"
    conn = gc()
    try:
        cur = conn.cursor()
        cur.execute(query, (user_id,))
        result = cur.fetchone()
        if result is not None:
            balance=result[0]
            return balance
        else:
            return None
    finally:
        cur.close()
        return_connection(conn)

def updateBalance(user_id, new_balance):
    """Updates the user's balance in the database."""
    
    query = "UPDATE users SET balance = %s WHERE user_id = %s"
    conn = gc()
    try:
        cur = conn.cursor()
        cur.execute(query, (new_balance, user_id))
        conn.commit()
    finally:
        cur.close()
        return_connection(conn)

def updateUsername(user_id, new_name):
    query = "UPDATE users SET user_name = %s WHERE user_id = %s"
    conn = gc()
    try:
        cur = conn.cursor()
        cur.execute(query, (new_name, user_id))
        conn.commit()
    finally:
        cur.close()
        return_connection(conn)

def updatePassword(user_id, new_password):
    query = "UPDATE users SET password = %s WHERE user_id = %s"
    conn = gc()
    try:
        cur = conn.cursor()
        cur.execute(query, (new_password, user_id))
        conn.commit()
    finally:
        cur.close()
        return_connection(conn)

