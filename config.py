"""
config.py
---------
Central configuration file for the Stocxsim application.

All sensitive credentials (passwords, API keys, TOTP secrets) are loaded
from `secrets.env` using python-dotenv so they are never hard-coded in source.

How to use:
    from config import API_KEY, POSTGRES
"""

import os
from dotenv import load_dotenv

# Load environment variables from the secrets file (never commit secrets.env to Git).
load_dotenv("secrets.env")

# -------------------------------------------------------------------
# PostgreSQL Database Connection Settings
# -------------------------------------------------------------------
POSTGRES = {
    "HOST": "localhost",       # Database server host (local dev)
    "PORT": 5432,              # Default PostgreSQL port
    "DB_NAME": "stocxsim",    # Name of the database schema
    "USER": "postgres",        # PostgreSQL username
    "PASSWORD": os.getenv("DB_PASSWORD")  # Loaded from secrets.env
}

# -------------------------------------------------------------------
# Angel One (SmartAPI) Broker Credentials
# Used for live market data subscription and WebSocket connection.
# -------------------------------------------------------------------
API_KEY = os.getenv("API_KEY")             # SmartAPI API key
CLIENT_ID = os.getenv("CLIENT_ID")         # Angel One client ID
CLIENT_PASSWORD = os.getenv("CLIENT_PASSWORD")  # Account password
TOTP_SECRET = os.getenv("TOTP_SECRET")    # TOTP secret for 2FA (pyotp)