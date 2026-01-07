
from time import time
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import json
from data.live_data import LIVE_PRICES, BASELINE_DATA, LIVE_STOCKS, LIVE_INDEX
from app import socketio
from config import API_KEY, CLIENT_ID
from utils.market_time import is_market_open


ws = None
subscribed_tokens = set()


def start_websocket(jwt_token, feed_token):
    global ws

    ws = SmartWebSocketV2(
        jwt_token,
        API_KEY,
        CLIENT_ID,
        feed_token
    )

    ws.on_open = on_open
    ws.on_data = on_data
    ws.on_error = on_error
    ws.on_close = on_close

    print("🚀 Connecting WebSocket...")
    ws.connect()

    return ws


def subscribe_user_watchlist(user_id, tokens):
    global ws, subscribed_tokens

    if ws is None:
        print("❌ WS not connected yet")
        return
    print(f"🔔 Subscribing user {user_id} watchlist:", tokens)

    for token in tokens:
        subscribe(ws, 1, token)  


def on_open(ws):
    print("🔗 WebSocket Connected")


def subscribe(ws, exchange, token):
    if token in subscribed_tokens:
        print(f"⚠️ Already subscribed {token}")
        return

    token_list = [
        {
            "exchangeType": exchange,
            "tokens": [token]
        }
    ]

    print("👉 Sending subscribe:", token_list)
    ws.subscribe("stockxsim",exchange, token_list)

    subscribed_tokens.add(token)
    print(f"✅ Subscribed to {token}")


def on_data(ws, message):
    token = message["token"]
    ltp = message["last_traded_price"] / 100

    print("📩 TICK:", token, ltp)


def on_error(ws, error):
    print("❌ WebSocket Error:", error)


def on_close(ws):
    print("🔴 WebSocket Closed")
