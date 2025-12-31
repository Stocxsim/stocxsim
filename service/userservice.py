from database.userdao import existUser

def login_service(email):
    user = existUser(email)
    return user
    