"""
main.py
-------
Application entry point for Stocxsim.

Startup sequence:
  1. Start the Angel One (SmartAPI) WebSocket connection in a background daemon
     thread so the app stays responsive even if the broker connection is slow.
  2. Launch Flask-SocketIO's development server on port 5000.

Run with:
    python main.py
"""

from app import app
from extensions import socketio
from service.angle_service import start_angel_one
import threading

if __name__ == "__main__":
    # -------------------------------------------------------------------
    # Step 1: Connect to Angel One (SmartAPI) broker in background.
    # daemon=True ensures this thread does not block the process from exiting.
    # -------------------------------------------------------------------
    angel_thread = threading.Thread(
        target=start_angel_one,
        daemon=True
    )
    angel_thread.start()

    # -------------------------------------------------------------------
    # Step 2: Start the Flask-SocketIO development server.
    # host="0.0.0.0" → accessible on the local network (not just 127.0.0.1).
    # use_reloader=False → prevents the Angel One thread from starting twice
    #                      (Flask's reloader forks the process).
    # -------------------------------------------------------------------
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )