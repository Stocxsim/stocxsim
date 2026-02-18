import os
from dotenv import load_dotenv

load_dotenv("secrets.env")

POSTGRES = {
    "HOST": "localhost",
    "PORT": 5432,
    "DB_NAME": "stocxsim",
    "USER": "postgres",
    "PASSWORD": os.getenv("DB_PASSWORD")
}

API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_PASSWORD  = os.getenv("CLIENT_PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")