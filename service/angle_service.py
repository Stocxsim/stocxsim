import pyotp
from SmartApi import SmartConnect

from config import API_KEY, CLIENT_ID, CLIENT_PASSWORD, TOTP_SECRET
from websockets.angle_ws import subscribe_user_watchlist;
from service.market_data_service import get_full_market_data
from data.live_data import BASELINE_DATA


def start_angel_one():
    print("🔐 Logging in to Angel One...")

    obj = SmartConnect(api_key=API_KEY)
    totp = pyotp.TOTP(TOTP_SECRET).now()

    session = obj.generateSession(CLIENT_ID, CLIENT_PASSWORD, totp)

    if not session or not session.get("status"):
        print("❌ Angel One Login Failed")
        return

    print("✅ Angel One Login Successful")

    TOKENS = ["99926000", "1594", "3045"]  # NIFTY, INFY, SBIN
    BASELINE_DATA.update(get_full_market_data(TOKENS))
    print("📊 Baseline data loaded")

    feed_token = obj.getfeedToken()
    jwt_token = session["data"]["jwtToken"]

    start_websocket(jwt_token, feed_token)
    print("🚀 Angel One WebSocket started")