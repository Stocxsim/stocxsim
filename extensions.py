"""
extensions.py
-------------
Flask extension instances that are initialised here and imported everywhere else.

Keeping extensions in a separate module breaks circular imports: the Flask app
object (app.py) and all blueprints can import `socketio` from here without
importing each other.

Usage:
    from extensions import socketio
    socketio.init_app(app)  # called once in app.py
"""

from flask_socketio import SocketIO

# Global SocketIO instance.
# - cors_allowed_origins="*"  → Allow all origins during development.
#   Restrict this to specific domains in production for security.
# - async_mode="threading"    → Uses Python's threading model; required when
#   running with Flask's built-in server (not eventlet/gevent).
socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)