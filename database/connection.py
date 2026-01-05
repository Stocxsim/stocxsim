import psycopg2
from config import POSTGRES


def get_connection():
    # Update these details with your actual database credentials
    conn = psycopg2.connect(
        dbname=POSTGRES["DB_NAME"],
        user=POSTGRES["USER"],
        password=POSTGRES["PASSWORD"],
        host=POSTGRES["HOST"],
        port=POSTGRES["PORT"]
    )
    print(POSTGRES["PORT"], POSTGRES["HOST"],
POSTGRES["DB_NAME"], POSTGRES["USER"])
    return conn
