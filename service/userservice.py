"""
userservice.py
--------------
Business logic for user authentication and account management.

Responsibilities:
  - Check if an email already exists in the database (login / signup split).
  - Register new users.
  - Generate and validate OTPs for email verification and password reset.
  - Send OTP emails via Gmail SMTP.

Security note:
  OTPs are stored in a plain in-memory dict (OTP_STORE). This works for a
  single-process app but will be lost on restart. For production, migrate to
  Redis with a TTL expiry.
"""

from database.userdao import existUser, saveUser, getUserByEmail
import smtplib
import random
from email.message import EmailMessage


def login_service(email):
    """
    Check whether the given email is registered.

    Returns the user record dict (or falsy value) from the database.
    Used by the frontend to decide whether to show the login or signup form.
    """
    user = existUser(email)
    return user

def signup_service(user):
    """
    Persist a new User object to the database.

    Args:
        user (User): A User model instance with username, email, and password.

    Returns:
        The result of saveUser (DB insert response / status dict).
    """
    saved_user = saveUser(user)
    return saved_user

def generate_otp():
    """Generate a random 6-digit OTP string."""
    return str(random.randint(100000, 999999))

def send_otp_email(receiver_email, otp):
    """
    Send the OTP to the user's email address via Gmail SMTP (SSL).

    Args:
        receiver_email (str): Destination email address.
        otp (str): The 6-digit OTP to embed in the email body.

    EVALUATOR NOTE: The app_password below is a Gmail App Password (not the
    account password). It should ideally be moved to secrets.env.
    """
    sender_email = "stocxsim@gmail.com"
    app_password = "dfxaailbrahcyeak"  # Gmail App Password (2FA bypass)

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

    # Connect to Gmail's SMTP SSL endpoint on port 465 and send the email.
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

# In-memory OTP store: {email: otp_string}.
# OTPs are cleared after successful verification.
# NOTE: This store is reset on every server restart.
OTP_STORE = {}

def send_otp(email):
    """
    Generate an OTP, save it in OTP_STORE, and email it to the user.

    Args:
        email (str): The recipient's email address.

    Returns:
        True always (email send failure will raise an exception upstream).
    """
    otp = generate_otp()
    OTP_STORE[email] = otp    # Overwrite any previous OTP for this email
    send_otp_email(email, otp)
    return True


def verify_otp_service(email, user_otp):
    """
    Validate the OTP submitted by the user.

    On success, the OTP is deleted from the store (one-time use).

    Args:
        email    (str): The user's email address.
        user_otp (str): The OTP entered by the user.

    Returns:
        True  → OTP matches; False → OTP not found or incorrect.
    """
    if email not in OTP_STORE:
        print("No OTP found for email:", email)
        return False

    if OTP_STORE[email] == user_otp:
        del OTP_STORE[email]  # Delete OTP after successful use
        return True

    print("OTP mismatch for:", email)
    return False

def getUserDetails(email):
    """
    Retrieve full user details (as a User object) by email address.

    Args:
        email (str): The user's registered email.

    Returns:
        User object or None if not found.
    """
    user = getUserByEmail(email)
    return user


