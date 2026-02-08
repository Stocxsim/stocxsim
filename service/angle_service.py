import pyotp
from SmartApi import SmartConnect

from config import API_KEY, CLIENT_ID, CLIENT_PASSWORD, TOTP_SECRET
from websockets.angle_ws import subscribe_user_watchlist;
from service.market_data_service import get_full_market_data
from data.live_data import BASELINE_DATA, INDEX_TOKENS, ensure_baseline_data
from service.market_data_service import load_baseline_data
from websockets.angle_ws import start_websocket

angel_started = False
angel_obj = None

def start_angel_one():
    global angel_started, angel_obj

    if angel_started:
        print("⚠️ Angel already started, skipping login")
        return

    print("🔐 Logging in to Angel One...")

    try:
        obj = SmartConnect(api_key=API_KEY)
        totp = pyotp.TOTP(TOTP_SECRET).now()
        session = obj.generateSession(CLIENT_ID, CLIENT_PASSWORD, totp)
    except Exception as e:
        print("❌ Angel login blocked / rate limited")
        print(str(e))
        return   # 👈 IMPORTANT: do NOT retry

    if not session or not session.get("status"):
        print("❌ Angel One Login Failed")
        return

    print("✅ Angel One Login Successful")

    angel_obj = obj
    angel_started = True

    # Seed index baseline (NIFTY + Sensex etc.) so UI can render without waiting for WS.
    try:
        ensure_baseline_data(INDEX_TOKENS)
        load_baseline_data()
    except Exception as e:
        print("⚠️ Index baseline seed failed:", e)

    feed_token = obj.getfeedToken()
    jwt_token = session["data"]["jwtToken"]

    # Force a clean WS boot on every app start (restart-safe).
    start_websocket(jwt_token, feed_token, force=True)
    print("🚀 Angel One WebSocket started")