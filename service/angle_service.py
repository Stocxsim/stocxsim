"""
service/angle_service.py
------------------------
Handles the initial connection and authentication with the Angel One (SmartAPI) broker.

This module is responsible for:
  1. Logging in to Angel One using TOTP-based 2FA authentication.
  2. Seeding baseline market data for NIFTY/SENSEX and other index tokens.
  3. Starting the WebSocket connection (angle_ws.py) for real-time price streaming.

Called once at startup from main.py in a background daemon thread.

Important:
  - angel_started flag prevents re-login if called multiple times (e.g., hot reload).
  - On login failure, the function exits immediately WITHOUT retrying to avoid
    AngelOne rate-limiting the credentials.
"""

import pyotp
from SmartApi import SmartConnect

from config import API_KEY, CLIENT_ID, CLIENT_PASSWORD, TOTP_SECRET
from websockets.angle_ws import subscribe_user_watchlist
from service.market_data_service import get_full_market_data
from data.live_data import BASELINE_DATA, INDEX_TOKENS, ensure_baseline_data
from service.market_data_service import load_baseline_data
from websockets.angle_ws import start_websocket

# Module-level guard to prevent duplicate Angel One login sessions.
angel_started = False
angel_obj = None

def start_angel_one():
    """
    Authenticate with Angel One and start the live WebSocket.

    Steps:
      1. Guard against duplicate startup (angel_started flag).
      2. Log in using API key + TOTP 2FA.
      3. Seed index (NIFTY/SENSEX) baseline data via REST so the dashboard
         renders immediately without waiting for the WebSocket.
      4. Start the Angel One WebSocket using JWT + feed tokens.
    """
    global angel_started, angel_obj

    if angel_started:
        print("⚠️ Angel already started, skipping login")
        return

    print("🔐 Logging in to Angel One...")

    try:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()  # Generate current TOTP code
        session = obj.generateSession(CLIENT_ID, CLIENT_PASSWORD, totp)
    except Exception as e:
        print("❌ Angel login blocked / rate limited")
        print(str(e))
        return   # Do NOT retry; Angel One will temporarily block repeated failed attempts

    if not session or not session.get("status"):
        print("❌ Angel One Login Failed")
        return

    print("✅ Angel One Login Successful")

    angel_obj = obj
    angel_started = True

    # Seed index baseline (NIFTY + Sensex etc.) so UI can render without waiting for WS.
    try:
        ensure_baseline_data(INDEX_TOKENS)  # Fetch baseline prices for index tokens
        load_baseline_data()                # Populate LIVE_INDEX with baseline values
    except Exception as e:
        print("⚠️ Index baseline seed failed:", e)

    feed_token = obj.getfeedToken()          # Required for WebSocket authentication
    jwt_token = session["data"]["jwtToken"]  # JWT used to identify the session

    # Force a clean WebSocket boot on every app start (restart-safe).
    start_websocket(jwt_token, feed_token, force=True)
    print("🚀 Angel One WebSocket started")