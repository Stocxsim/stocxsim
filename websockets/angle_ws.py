
from time import time
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import json
from data.live_data import LIVE_PRICES, BASELINE_DATA, LIVE_STOCKS, LIVE_INDEX
from app import socketio
from config import API_KEY, CLIENT_ID
from utils.market_time import is_market_open



subscribed_tokens = set()
ws = None


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


def on_open(ws):
    print("🔗 WebSocket Connected")

    # Subscribe when socket opens
    subscribe(ws,1,"99926009")  # BANKNIFTY
    subscribe(ws,1,"99926013")  # FINNIFTY
    subscribe(ws,2,"99919000")    # SENSEX
    subscribe(ws, 1, "99926000")   # NIFTY


def subscribe(ws, exchange, token):
    if token in subscribed_tokens:
        print(f"⚠️ Already subscribed {token}")
        return

    payload = {
        "correlationID": "stockxsim",
        "action": 1,
        "params": {
            "mode": 1,
            "tokenList": [
                {
                    "exchangeType": exchange,
                    "tokens": [token]
                }
            ]
        }
    }

    print("👉 Sending subscribe:", payload)
    ws.send(json.dumps(payload))

    subscribed_tokens.add(token)
    print(f"✅ Subscribed to {token}")



def on_data(ws, message):
    # if not is_market_open():
    #     return   # ❌ ignore WS ticks when market closed
    token = message["token"]
    ltp = message["last_traded_price"] / 100

    base = BASELINE_DATA.get(token, {}).get("prev_close")

    change = ltp - base
    percent = (change / base) * 100 if base else 0

    data = {
        "ltp": round(ltp, 2),
        "change": round(change, 2),
        "percent": round(percent, 2)
    }

    # dict update
    LIVE_PRICES[token] = ltp
    if token.startswith("999"):
        LIVE_INDEX[token] = data
    else:
        LIVE_STOCKS[token] = data

    # 🔥 FULL dict push
    print("🔥 EMIT DATA:", {
    "stocks": LIVE_STOCKS,
    "index": LIVE_INDEX
})

    socketio.emit("live_prices", {
        "stocks": LIVE_STOCKS,
        "index": LIVE_INDEX
    })
    


def on_error(ws, error):
    print("❌ WebSocket Error:", error)


def on_close(ws):
    print("🔴 WebSocket Closed")