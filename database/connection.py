import psycopg2
from psycopg2 import pool
from config import POSTGRES

# Create a connection pool (reuse connections instead of creating new ones)
connection_pool = None

def init_pool():
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # minconn
            10, # maxconn
            dbname=POSTGRES["DB_NAME"],
            user=POSTGRES["USER"],
            password=POSTGRES["PASSWORD"],
            host=POSTGRES["HOST"],
            port=POSTGRES["PORT"]
        )

def get_connection():
    """Get connection from pool instead of creating new ones"""
    global connection_pool
    if connection_pool is None:
        init_pool()
    return connection_pool.getconn()

def return_connection(conn):
    """Return connection back to pool"""
    global connection_pool
    if connection_pool is not None:
        connection_pool.putconn(conn)
