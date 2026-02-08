
from time import time
import threading
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import json
from data.live_data import BASELINE_DATA, LIVE_STOCKS, LIVE_INDEX, INDEX_TOKENS
from app import socketio
from config import API_KEY, CLIENT_ID
from utils.market_time import is_market_open


ws = None
ws_connected = False
subscribed_tokens = set()
_last_credentials = {"jwt": None, "feed": None}
_reconnect_timer = None
last_emit_time = 0
EMIT_THROTTLE_MS = 100  # Emit max every 100ms to reduce network overhead


def is_ws_connected() -> bool:
    return bool(ws is not None and ws_connected)


def reset_ws_state() -> None:
    """Best-effort close existing WS and clear in-memory flags.

    This prevents old/stale WS state from affecting a new login/app restart.
    """
    global ws, ws_connected, subscribed_tokens

    try:
        if ws is not None:
            ws.close()
    except Exception:
        pass

    ws = None
    ws_connected = False
    subscribed_tokens.clear()


def start_websocket(jwt_token, feed_token, force: bool = False):
    global ws, _last_credentials

    _last_credentials = {"jwt": jwt_token, "feed": feed_token}

    if force:
        reset_ws_state()

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
    try:
        ws.connect()
    except Exception as e:
        print("❌ WebSocket connect failed:", e)
        _schedule_reconnect()

    return ws


def subscribe_user_watchlist(user_id, tokens):
    global ws, subscribed_tokens

    if ws is None:
        print("❌ WS not connected yet")
        return
    print(f"🔔 Subscribing user {user_id} watchlist:", tokens)

    for token in tokens:
        subscribe(ws, 1, token)


def subscribe_equity_tokens(tokens):
    """Subscribe additional equity tokens (e.g., holdings) if WS is connected."""
    global ws

    if ws is None:
        return

    for token in tokens:
        if token is None:
            continue
        subscribe(ws, 1, str(token))


def on_open(ws):
    global ws_connected
    ws_connected = True
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
    ws.subscribe("stockxsim", exchange, token_list)

    subscribed_tokens.add(token)
    print(f"✅ Subscribed to {token}")


def unsubscribe(ws, exchange, token):
    global subscribed_tokens

    if token not in subscribed_tokens:
        print(f"⚠️ Not subscribed {token}, skipping unsubscribe")
        return

    token_list = [
        {
            "exchangeType": exchange,
            "tokens": [token]
        }
    ]

    print("👈 Sending unsubscribe:", token_list)
    ws.unsubscribe("stockxsim", exchange, token_list)

    subscribed_tokens.remove(token)
    print(f"❌ Unsubscribed from {token}")


def on_data(ws, message):
    try:
        global last_emit_time
        token = message["token"]
        ltp = message["last_traded_price"] / 100

        base = BASELINE_DATA.get(token)
        if base and 'prev_close' in base:
            data = {
                "ltp": ltp,
                "change": round(ltp - base['prev_close'], 2),
                "percent_change": round(((ltp - base['prev_close']) / base['prev_close']) * 100, 2)
            }
            
            if token in INDEX_TOKENS:
                LIVE_INDEX[token].update(data)
            else:
                LIVE_STOCKS[token].update(data)
        else:
            # If no base, just update the LTP so the UI at least shows the price
            if token in INDEX_TOKENS:
                LIVE_INDEX[token]['ltp'] = ltp
            else:
                LIVE_STOCKS[token]['ltp'] = ltp

        # Throttle emissions to reduce network overhead
        current_time = time() * 1000
        if current_time - last_emit_time > EMIT_THROTTLE_MS:
            last_emit_time = current_time
            socketio.emit("live_prices", {
                "stocks": LIVE_STOCKS,
                "index": LIVE_INDEX
            })

    except Exception as e:
        print("WS ERROR:", e)


def on_error(ws, error):
    global ws_connected
    ws_connected = False
    print("❌ WebSocket Error:", error)
    _schedule_reconnect()


def on_close(ws):
    global ws_connected
    ws_connected = False
    print("🔴 WebSocket Closed")
    _schedule_reconnect()


def _schedule_reconnect() -> None:
    """Reconnect with a small delay; never block login or request threads."""
    global _reconnect_timer

    if _reconnect_timer is not None and _reconnect_timer.is_alive():
        return

    jwt_token = _last_credentials.get("jwt")
    feed_token = _last_credentials.get("feed")
    if not jwt_token or not feed_token:
        return

    def _do():
        global _reconnect_timer
        _reconnect_timer = None
        start_websocket(jwt_token, feed_token, force=True)

    _reconnect_timer = threading.Timer(2.0, _do)
    _reconnect_timer.daemon = True
    _reconnect_timer.start()
