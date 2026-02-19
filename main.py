# main.py

from app import app
from extensions import socketio
from service.angle_service import start_angel_one
import threading

if __name__ == "__main__":
    # ---------------- START ANGEL ONE ----------------
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