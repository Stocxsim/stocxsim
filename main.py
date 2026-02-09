# main.py

from app import app
from extensions import socketio
from service.angle_service import start_angel_one
import threading

if __name__ == "__main__":
    #  # ---------------- MARKET CLOSED → OFFLINE MODE ----------------
    # if not is_market_open():
    #     print("🌙 Market CLOSED → OFFLINE MODE")

    #     print(BASELINE_DATA)

    #     # 🔥 Emit once so frontend shows last data
    #     socketio.emit("live_prices", {
    #         "index": BASELINE_DATA
    #     })

    # # ---------------- MARKET OPEN → ONLINE MODE ----------------
    # else:
    print("☀️ Market OPEN → LIVE MODE")

    angel_thread = threading.Thread(
        target=start_angel_one,
        daemon=True
    )
    angel_thread.start()

    # ---------------- START FLASK ----------------
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )