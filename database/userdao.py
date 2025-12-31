# from database.connection import getConnection as gc
def existUser(email):
    # query = "SELECT * FROM users WHERE email = %s"
    # cur=gc().cursor()
    # cur.execute(query, (email,))
    # result = cur.fetchone()
    # if result is not None:
    #     query="SELECT password FROM users WHERE email=%s"
    #     cur.execute(query,(email,))
    #     password=cur.fetchone()
        
    #     return {"message":True,"password":password[0]}
    # else:
    #     return {"message":False,"password":None}
    return {"message":False,"password":None}