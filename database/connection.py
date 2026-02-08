import psycopg2
from psycopg2 import pool
from config import POSTGRES
import threading

# Thread-safe connection pool
connection_pool = None
_pool_lock = threading.Lock()

def init_pool():
    global connection_pool
    if connection_pool is not None:
        return

    # Guard against multi-threaded init races: if two threads create pools,
    # returning a connection to a different pool raises PoolError.
    with _pool_lock:
        if connection_pool is not None:
            return
        try:
            # ThreadedConnectionPool is required for multi-threaded Flask apps
            connection_pool = psycopg2.pool.ThreadedConnectionPool(
                1,   # minconn: minimum connections kept open
                20,  # maxconn: increased to 20 to prevent exhaustion
                dbname=POSTGRES["DB_NAME"],
                user=POSTGRES["USER"],
                password=POSTGRES["PASSWORD"],
                host=POSTGRES["HOST"],
                port=POSTGRES["PORT"]
            )
            print("✅ Database connection pool initialized")
        except Exception as e:
            print(f"❌ Failed to initialize pool: {e}")

def get_connection():
    """Get connection from pool"""
    global connection_pool
    if connection_pool is None:
        init_pool()
    return connection_pool.getconn()

def return_connection(conn):
    """Return connection back to pool"""
    global connection_pool
    if connection_pool is not None and conn is not None:
        try:
            connection_pool.putconn(conn)
        except pool.PoolError as e:
            # Most commonly caused by init race or double-return; best effort cleanup.
            print(f"⚠️ DB pool return warning: {e}")
            try:
                conn.close()
            except Exception:
                pass