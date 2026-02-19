from database.userdao import existUser,saveUser, getUserByEmail
import smtplib
import random
from email.message import EmailMessage


def login_service(email):
    user = existUser(email)
    return user

def signup_service(user):
    saved_user = saveUser(user)
    return saved_user

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(receiver_email, otp):
    sender_email = "stocxsim@gmail.com"
    app_password = "dfxaailbrahcyeak"

    msg = EmailMessage()
    msg["Subject"] = "Your OTP Verification Code"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 5 minutes.
Do not share this OTP with anyone.

Thanks,
Stocxsim Team
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

OTP_STORE = {}

def send_otp(email):
    otp = generate_otp()
    OTP_STORE[email] = otp
    send_otp_email(email, otp)
    return True


def verify_otp_service(email, user_otp):
    if email not in OTP_STORE:
        print("No OTP found for email:", email)
        return False

    if OTP_STORE[email] == user_otp:
        del OTP_STORE[email] 
        return True
    
    print("None of the above")
    return False

def getUserDetails(email):
    user = getUserByEmail(email)
    return user


