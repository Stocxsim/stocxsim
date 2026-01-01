from database.connection import get_connection as gc

def existUser(email):
    query = "SELECT * FROM users WHERE email = %s"
    cur=gc().cursor()
    cur.execute(query, (email,))
    result = cur.fetchone()
    if result is not None:
        query="SELECT password FROM users WHERE email=%s"
        cur.execute(query,(email,))
        password=cur.fetchone()
        
        return {"message":True,"password":password[0]}
    else:
        return {"message":False,"password":None}
    
def saveUser(user):
    try:
        conn = gc()
        cur = conn.cursor()

        query = """
        INSERT INTO users (name, email, password)
        VALUES (%s, %s, %s)
        """

        cur.execute(query, (user.username, user.email, user.password))
        conn.commit()

        return {"message": True}

    except Exception as e:
        print("DB Error:", e)
        return {"message": False}

    finally:
        cur.close()
        conn.close()