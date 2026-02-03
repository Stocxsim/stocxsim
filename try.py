import psycopg2
import csv

conn = psycopg2.connect(
    dbname="stocxsim",
    user="postgres",
    password="Ap1420@810",
    host="localhost",
    port=5432
)

cur = conn.cursor()

# 1️⃣ Temp table with Angel One tokens
cur.execute("""
CREATE TEMP TABLE temp_angel_tokens (
    token TEXT PRIMARY KEY
)
""")

# 2️⃣ Load Angel One token list into temp table
with open("angel_token_with_full_name.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cur.execute(
            "INSERT INTO temp_angel_tokens (token) VALUES (%s) ON CONFLICT DO NOTHING",
            (row["token"],)
        )

# 3️⃣ DELETE stocks not present in Angel One 🔥
cur.execute("""
DELETE FROM stocks
WHERE stock_token NOT IN (
    SELECT token FROM temp_angel_tokens
)
""")

deleted_rows = cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"✅ Cleanup done. Deleted rows: {deleted_rows}")
